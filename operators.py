from .functions import latlon_to_xyz, create_flat_face, create_building, calculate_horizontal_area, calculate_and_group_vertical_faces
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
            calculate_horizontal_area(cube, threshold=0.01)
            calculate_and_group_vertical_faces(cube, threshold=0.01, angle_tolerance=30)
            print(cube.my_properties.usage)
            print(cube.my_properties.age)

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
                continue

            # Print the selected archetype description
            print(f"Selected Archetype: {selected_archetype['description']}")

            # Get construction data for the selected archetype
            constructions = selected_archetype['constructions']
            for construction_type, properties in constructions.items():
                print(f"\n{construction_type.capitalize()}:")

                # Extract and display U-value and k_m
                u_value = properties["Uvalue"]
                k_m = properties["k_m"]
                print(f"  U-value: {u_value:.2f} W/(m²·K)")
                print(f"  k_m: {k_m:.2f} J/(m²·K)")

                # If it's a window, also print g-factor and wwr
                if construction_type == "window":
                    g_factor = properties["g-factor"]
                    wwr = properties["wwr"]
                    print(f"  g-factor: {g_factor:.2f}")
                    print(f"  wwr: {wwr:.2f}")

        return {'FINISHED'}
