from .functions import latlon_to_xyz, create_flat_face, create_building, calculate_horizontal_area, calculate_and_group_vertical_faces, process_archetype
import bpy
import json
import os


class ADDON1_OT_Operator(bpy.types.Operator):
    bl_label = "Import geojson file"
    bl_idname = "import.myop_operator"

    def execute(self, context):
        # Load the JSON file
        json_path = "/Users/alm/Documents/arcade/myfile3.geojson"  # Replace with your file path
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Find the vertex with the smallest latitude and longitude
        min_lat = float('inf')
        min_lon = float('inf')

        # Iterate through all features to find the smallest lat/lon
        latitudes = []

        for feature in data['features']:
            coordinates = feature['geometry']['coordinates']
            for polygon in coordinates:
                for point in polygon:
                    latitudes.append(point[1])  # latitude is the second value in the coordinate

        # Find the minimum latitude
        min_lat = min(latitudes)


        longitudes = []

        for feature in data['features']:
            coordinates = feature['geometry']['coordinates']
            for polygon in coordinates:
                for point in polygon:
                    longitudes.append(point[0])  # latitude is the second value in the coordinate

        # Find the minimum latitude
        min_lon = min(longitudes)


        # Iterate through the features in the JSON and create buildings or flat faces
        for feature in data['features']:
            coordinates = feature['geometry']['coordinates'][0]
            height = feature['properties'].get('building:levels', "NA")
            year = feature['properties'].get('start_date', "NA")
            use = feature['properties'].get('building', "NA")


            # Convert lat/lon to Blender coordinates, using the smallest lat/lon as the origin
            vertices = [latlon_to_xyz(lat, lon, min_lat, min_lon) for lon, lat in coordinates]

            # If height is "NA" or not defined, create a flat face
            if height == "NA" or not height.isdigit():
                create_flat_face(vertices, f"Flat_{feature['properties']['id']}")
            else:
                # Otherwise, create a building with the given height
                height = float(height)  # Convert height to float
                year = int(year)  # Convert year to int
                create_building(vertices, height*3, f"Building_{feature['properties']['@id']}", year, use)



        print("Buildings created successfully.")
        return {'FINISHED'}  # Or another appropriate result like {'CANCELLED'}


class ADDON2_OT_Operator(bpy.types.Operator):
    bl_label = "Calculate Heating and Cooling Loads"
    bl_idname = "calculate.myop_operator"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        addon_directory = os.path.dirname(os.path.realpath(__file__))

        # Load the JSON file
        def load_json(file_name):
            file_path = os.path.join(addon_directory, file_name)
            with open(file_path, 'r') as file:
                return json.load(file)

        # Load the archetypes.json file
        archetype_data = load_json('archetypes.json')

        for cube in selected_objects:

            #Calculate the horizontal area of the building
            horizontal_face_area=calculate_horizontal_area(cube, threshold=0.01)

            #Calculate the vertical areas of the building together with their orientation
            vertical_faces_areas=calculate_and_group_vertical_faces(cube, threshold=0.01, angle_tolerance=30)

            #Calculate total sum of vertical areas
            tot_vertical_area=sum(vertical_faces_areas.values())

            #Process the archetypes JSON file to match the archetype
            process_archetype(cube, archetype_data)
            print(cube.my_properties.usage)
            print(cube.my_properties.age)
            constructions_data=process_archetype(cube, archetype_data)
            print(constructions_data)

            #Calculate the total heat capacity of the building (windows are not involved - Eq. 66)
            Cm_floor=constructions_data.get("floor")["k_m"]*horizontal_face_area
            Cm_roof=constructions_data.get("roof")["k_m"]*horizontal_face_area
            Cm_walls=constructions_data.get("walls")["k_m"]*tot_vertical_area*(1-constructions_data.get("window")["wwr"])
            Cm_tot=Cm_floor+Cm_roof+Cm_walls

            #Calculate the effective mass area Am - Eq. 65)
            den_floor=constructions_data.get("floor")["k_m"]**2*horizontal_face_area
            den_roof=constructions_data.get("roof")["k_m"]**2*horizontal_face_area
            den_walls=constructions_data.get("walls")["k_m"]**2*tot_vertical_area*(1-constructions_data.get("window")["wwr"])
            Am=Cm_tot**2/(den_floor+den_roof+den_walls)
            print(horizontal_face_area)
            print(Cm_floor)
            print(Cm_roof)
            print(Cm_walls)
            print(den_floor)
            print(Am)

            #Calculate the total haet capacity Cm




        return {'FINISHED'}
