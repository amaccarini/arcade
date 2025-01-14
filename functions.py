import bpy
import json
import bmesh
from math import pi, cos, degrees, atan2
from mathutils import Vector
import requests
import pandas as pd
import os

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


    if use == "detached" or use =="terrace" or use == "house" or use =="residential" or use =="apartments" or use=="semidetached_house":
        obj.my_properties.usage = "RES"
    elif use == "office" or use =="commercial":
        obj.my_properties.usage = "COM"
    else:
        obj.my_properties.usage = "RES"


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

#Function to process archetypes
def process_archetype(cube, archetype_data, archetype_country):
    """
    Determines the archetype name based on the cube's properties, the input country,
    and returns relevant construction details (U-values, k_m, g-factor, wwr).

    Args:
        cube: The selected Blender object with `my_properties.usage` and `my_properties.age`.
        archetype_data: Loaded JSON data containing archetype information.
        country (str): The country for the archetype (e.g., 'DK', 'US_2A', 'US_3C', 'US_5A').

    Returns:
        dict: The matching archetype's constructions, or None if not found.
    """
    # Extract building properties from the cube
    building_type = cube.my_properties.usage  # Either 'RES_1' or 'COM_1'
    year = cube.my_properties.age             # Building construction year

    # Validate building_type
    if building_type not in ["RES_1", "COM_1"]:
        print(f"Invalid building type '{building_type}'. Must be 'RES_1' or 'COM_1'.")
        return None

    # Validate country
    if archetype_country not in ["DK", "US_2A", "US_3C", "US_5A"]:
        print(f"Invalid country '{archetype_country}'. Must be one of ['DK', 'US_2A', 'US_3C', 'US_5A'].")
        return None

    # Determine the year range based on the country
    if archetype_country == "DK":
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
    elif archetype_country in ["US_2A", "US_3C", "US_5A"]:  # US Regions
        if year < 1980:
            year_range = "1980"
        elif 1980 <= year < 2004:
            year_range = "1980_2004"
        else:
            year_range = "2004"
    else:
        print(f"Country '{archetype_country}' not supported.")
        return None

    # Construct the archetype name
    archetype_name = f"{building_type}_{year_range}_{archetype_country}"

    # Find the matching archetype
    selected_archetype = None
    for archetype in archetype_data['archetypes']:
        if archetype['name'] == archetype_name:
            selected_archetype = archetype
            break

    # Handle missing archetypes
    if not selected_archetype:
        print(f"Archetype '{archetype_name}' not found!")
        return None  # Stop processing if no matching archetype is found

    # Return the constructions from the selected archetype
    return selected_archetype['constructions']



# Function to fetch buildings GeoJSON
import requests
import json
import numpy as np

def fetch_buildings_geojson(bbox, output_folder, start_date_mean, start_date_std_dev, levels_mean, levels_std_dev):
    """
    Fetch buildings within a specified bounding box from Overpass API, enrich with probabilistic properties,
    and save as GeoJSON.

    Args:
        bbox (tuple): Bounding box in the format (south, west, north, east).
        output_folder (str): Path to the folder where the GeoJSON file will be saved.
        start_date_mean (int): Mean year for start_date normal distribution.
        start_date_std_dev (int): Standard deviation for start_date normal distribution.
        levels_mean (float): Mean levels for building:levels normal distribution.
        levels_std_dev (float): Standard deviation for building:levels normal distribution.

    Returns:
        str: Result message indicating success or error.
    """
    # Overpass API endpoint
    overpass_url = "https://overpass-api.de/api/interpreter"

    # Overpass query
    query = f"""
    [out:json][timeout:25];
    (
      way["building"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
      relation["building"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    );
    out body;
    >;
    out skel qt;
    """

    try:
        print("Sending request to Overpass API...")
        response = requests.get(overpass_url, params={"data": query})

        if response.status_code == 200:
            print("Response received. Parsing data...")
            data = response.json()

            # Convert Overpass JSON to GeoJSON
            geojson = {
                "type": "FeatureCollection",
                "features": []
            }

            # Parse nodes and ways to construct polygons
            nodes = {node["id"]: (node["lon"], node["lat"]) for node in data.get("elements", []) if node["type"] == "node"}
            for element in data.get("elements", []):
                if element["type"] == "way" and "nodes" in element:
                    coordinates = [nodes[node_id] for node_id in element["nodes"] if node_id in nodes]
                    if len(coordinates) > 2:  # Ensure it forms a polygon
                        feature = {
                            "type": "Feature",
                            "properties": element.get("tags", {}),
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [coordinates]
                            },
                            "id": element["id"]
                        }
                        geojson["features"].append(feature)

            # Enrich missing properties
            enrich_features(geojson["features"], start_date_mean, start_date_std_dev, levels_mean, levels_std_dev)

            # Save the enriched GeoJSON to file
            output_file = f"{output_folder}/enriched_buildings.geojson"
            with open(output_file, "w") as f:
                json.dump(geojson, f, indent=4)

            return f"Enriched GeoJSON data saved to {output_file}"
        else:
            return f"Error: Unable to fetch data. HTTP Status code: {response.status_code}"

    except Exception as e:
        return f"Error occurred: {str(e)}"


def enrich_features(features, start_date_mean, start_date_std_dev, levels_mean, levels_std_dev):
    """
    Enrich features by assigning missing start_date and building:levels properties.

    Args:
        features (list): List of GeoJSON features.
        start_date_mean (int): Mean year for start_date normal distribution.
        start_date_std_dev (int): Standard deviation for start_date normal distribution.
        levels_mean (float): Mean levels for building:levels normal distribution.
        levels_std_dev (float): Standard deviation for building:levels normal distribution.
    """
    for feature in features:
        # Assign missing start_date
        if "start_date" not in feature["properties"] or not feature["properties"]["start_date"]:
            start_date = int(np.random.normal(start_date_mean, start_date_std_dev))
            if start_date < 1850:
                start_date = 1850
            elif start_date > 2024:
                start_date = 2024
            feature["properties"]["start_date"] = str(start_date)

        # Assign missing building:levels
        if "building:levels" not in feature["properties"] or not feature["properties"]["building:levels"]:
            levels = max(1, round(np.random.normal(levels_mean, levels_std_dev)))  # Ensure at least 1 level
            feature["properties"]["building:levels"] = str(levels)

        # Ensure the "building" key is set appropriately
        if "building" not in feature["properties"] or feature["properties"]["building"] == "yes":
            feature["properties"]["building"] = "residential"


def get_csv_column(file_path, column_name):
    """
    Reads a specific column from a CSV file and returns its values as a list.

    Args:
        file_path (str): The path to the CSV file.
        column_name (str): The name of the column to retrieve.

    Returns:
        list: The values of the specified column as a list.

    Raises:
        FileNotFoundError: If the file is not found.
        KeyError: If the column name is not found in the file.
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    # Read the CSV file
    df = pd.read_csv(file_path)

    # Check if the column exists
    if column_name not in df.columns:
        raise KeyError(f"The column '{column_name}' does not exist in the file '{file_path}'.")

    # Return the column values as a list
    return df[column_name].tolist()
