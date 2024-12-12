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
    if use == "detached":
        obj.my_properties.usage = "detached"
    elif use == "terrace":
        obj.my_properties.usage = "terrace"
    else:
        obj.my_properties.usage = "apartments"

# Function to calculate horizontal surface for buildings (floor and roof surface area)
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
    print(horizontal_area)



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

    print(grouped_faces)
