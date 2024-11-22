import bpy
import json
from math import pi, cos
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
