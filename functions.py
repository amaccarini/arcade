import bpy
import json
import bmesh
from math import pi, cos, degrees, atan2
from mathutils import Vector

# Earth radius and scale (in meters)
EARTH_RADIUS = 6371000  # in meters

def latlon_to_xyz(lat, lon, origin_lat, origin_lon, scale=1):
    """ Convert lat/lon to Blender 3D coordinates based on an origin point.
    Treating the region as locally flat for small areas using basic projection.

    Parameters:
        lat, lon: The latitude and longitude of the point.
        origin_lat, origin_lon: The origin latitude and longitude to center the map.
        scale: Scaling factor to adjust the size of the projection in Blender.
    """
    # Calculate deltas from the origin (in meters)
    lat_diff = (lat - origin_lat) * (pi / 180) * EARTH_RADIUS
    lon_diff = (lon - origin_lon) * (pi / 180) * EARTH_RADIUS * cos(origin_lat * pi / 180)

    # Return scaled x, y coordinates for Blender
    return lon_diff * scale, lat_diff * scale

# Function to create a flat face (no height)
def create_flat_face(vertices, name):
    """ Create a flat polygon mesh in Blender from a list of 2D vertices. """
    base_verts = [Vector((v[0], v[1], 0)) for v in vertices]
    num_verts = len(base_verts)

    # Create a single face from the vertices
    faces = [list(range(num_verts))]

    # Create the mesh
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(base_verts, [], faces)
    mesh.update()

    # Create an object and link it to the scene
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

# Function to create a building mesh from a list of vertices and height (extruded)
def create_building(vertices, height, name, year, use):
    """ Create a building mesh in Blender from a list of 2D vertices and a height. """
    # Create 3D vertices with base height at 0
    base_verts = [Vector((v[0], v[1], 0)) for v in vertices]
    top_verts = [Vector((v[0], v[1], height)) for v in vertices]

    # Define the faces
    faces = []
    num_verts = len(base_verts)

    # Side faces
    for i in range(num_verts):
        next_i = (i + 1) % num_verts
        face = [i, next_i, next_i + num_verts, i + num_verts]
        faces.append(face)

    # Bottom face
    faces.append([i for i in range(num_verts)])

    # Top face
    faces.append([i + num_verts for i in range(num_verts)])

    # Create the mesh
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(base_verts + top_verts, [], faces)
    mesh.update()

    # Create an object and link it to the scene
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.my_properties.age = year
    if use == "detached" or use =="terrace" or use == "house" or use =="residential" or use=="semidetached_house":
        obj.my_properties.usage = "SFH"
    elif use == "apartments":
        obj.my_properties.usage = "AB"
    else:
        obj.my_properties.usage = "OTH"

# Function to calculate horizontal surface of buildings (floor and roof surface area - divided by 2 to get single surface)
def calculate_horizontal_area(obj, threshold=0.01):
    """
    Calculate the horizontal surface area of a mesh object in Blender.

    Parameters:
        obj (bpy.types.Object): The mesh object to calculate the area for.
        threshold (float): Tolerance for determining if a face is horizontal
                           (normal.z close to ±1).

    Returns:
        float: The horizontal surface area in square meters.
    """
    if obj.type != 'MESH':
        print(f"{obj.name} is not a mesh object!")
        return 0.0

    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Get the mesh data
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    horizontal_area = 0.0
    threshold = 0.01

    # Loop through all faces in the mesh
    for face in bm.faces:
        # Get the face normal
        normal = face.normal.normalized()
        # Check if the face is horizontal
        if abs(normal.z) >= (1 - threshold):  # Nearly horizontal
            horizontal_area += face.calc_area()/2
    return horizontal_area



def calculate_and_group_vertical_faces(obj, threshold=0.01, angle_tolerance=30):
    """
    Calculate and group vertical faces of a mesh object in Blender by similar rotation angles.

    Parameters:
        obj (bpy.types.Object): The mesh object to calculate the areas for.
        threshold (float): Tolerance for determining if a face is vertical
                           (normal.z close to 0).
        angle_tolerance (float): Maximum difference in rotation angles (degrees) to group faces.

    Returns:
        dict: A dictionary where keys are the rounded rotation angles (group centers) and
              values are the total area of faces in that group.
    """
    if obj.type != 'MESH':
        print(f"{obj.name} is not a mesh object!")
        return {}
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # Get the mesh data
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    vertical_faces = []

    # Z-axis for vertical comparison
    z_axis = Vector((0, 0, 1))

    # Loop through all faces in the mesh
    for face in bm.faces:
        # Get the face normal
        normal = face.normal.normalized()

        # Check if the face is vertical (normal.z is close to 0)
        if abs(normal.z) <= threshold:  # Nearly vertical
            # Calculate area
            area = face.calc_area()

            # Calculate orientation (rotation angle in degrees around Z-axis)
            horizontal_projection = Vector((normal.x, normal.y))
            angle = degrees(atan2(horizontal_projection.y, horizontal_projection.x))

            # Normalize angle to range [0, 360)
            angle = angle % 360

            # Add face information to the list
            vertical_faces.append({
                "area": area,
                "orientation": angle
            })

    bm.free()

    # Group faces by similar angles (within angle_tolerance)
    grouped_faces = {}
    for face_info in vertical_faces:
        area = face_info["area"]
        angle = face_info["orientation"]

        # Find the closest group center or create a new group
        group_found = False
        for group_angle in grouped_faces:
            if abs(group_angle - angle) <= angle_tolerance:
                grouped_faces[group_angle] += area
                group_found = True
                break

        if not group_found:
            grouped_faces[angle] = area

    rounded_grouped_faces = {round(k, 1): round(v, 1) for k, v in grouped_faces.items()}
    return rounded_grouped_faces


def process_archetype(cube, archetype_data):
    """
    Determines the archetype name based on the cube's properties, finds the matching archetype,
    and prints relevant details including U-values, k_m, g-factor, and wwr.

    Args:
        cube: The selected Blender object with `my_properties.usage` and `my_properties.age`.
        archetype_data: Loaded JSON data containing archetype information.
    """
    # Define the building properties
    building_type = "SFH" if cube.my_properties.usage == "SFH" else "AB"
    year = cube.my_properties.age  # Building year
    country = "DK"

    # Determine the year range
    if year < 1850:
        year_range = "1850"
    elif 1851 <= year <= 1930:
        year_range = "1851_1930"
    elif 1931 <= year <= 1950:
        year_range = "1931_1950"
    elif 1951 <= year <= 1960:
        year_range = "1951_1960"
    elif 1961 <= year <= 1972:
        year_range = "1961_1972"
    elif 1973 <= year <= 1978:
        year_range = "1973_1978"
    elif 1979 <= year <= 1998:
        year_range = "1979_1998"
    elif 1999 <= year <= 2006:
        year_range = "1999_2006"
    elif 2007 <= year <= 2010:
        year_range = "2007_2010"
    else:
        year_range = "2011"

    # Construct the archetype name
    archetype_name = f"{building_type}_{year_range}_{country}"

    # Find the matching archetype
    selected_archetype = None
    for archetype in archetype_data['archetypes']:
        if archetype['name'] == archetype_name:
            selected_archetype = archetype
            break

    if not selected_archetype:
        print(f"Archetype '{archetype_name}' not found!")
        return  None # Stop processing this cube if no matching archetype is found


    return selected_archetype['constructions']
