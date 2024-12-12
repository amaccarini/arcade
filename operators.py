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
    bl_label = "calculate heating and cooling laods"
    bl_idname = "calculate.myop_operator"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        for cube in selected_objects:
            calculate_horizontal_area(cube, threshold=0.01)
            calculate_and_group_vertical_faces(cube, threshold=0.01, angle_tolerance=30)
            print(cube.my_properties.usage)
            print(cube.my_properties.age)

            addon_directory = os.path.dirname(os.path.realpath(__file__))
            print(addon_directory)

            # Load JSON data from the files
            def load_json(file_name):
                file_path = os.path.join(addon_directory, file_name)
                with open(file_path, 'r') as file:
                    return json.load(file)

            # Load the JSON files
            archetype_data = load_json('archetypes.json')
            construction_data = load_json('constructions.json')
            material_data = load_json('materials.json')

            # Define the building properties
            building_type = "SFH"
            year = cube.my_properties.age  # Change this year as needed
            country = "DK"

            # Construct the archetype name based on the year
            if year < 1850:
                year_range = "1850"
            elif 1851 <= year <= 1930:
                year_range = "1851_1930"
            else:
                year_range = "1931_1950"

            archetype_name = f"{building_type}_{year_range}_{country}"

            # Find the matching archetype
            selected_archetype = None
            for archetype in archetype_data['archetypes']:
                if archetype['name'] == archetype_name:
                    selected_archetype = archetype
                    break

            if not selected_archetype:
                print(f"Archetype '{archetype_name}' not found!")
                exit()

            print(f"Selected Archetype: {selected_archetype['description']}")

            # Get the construction types for the archetype
            constructions = selected_archetype['constructions']

            # Extract construction details
            for construction_type, construction_name in constructions.items():
                print(f"\n{construction_type.capitalize()} - {construction_name}")

                # Find the construction layers
                construction = next((c for c in construction_data['constructions'] if c['name'] == construction_name), None)
                if not construction:
                    print(f"  No details found for {construction_name}")
                    continue

                print("  Layers:")
                total_resistance = 0  # Initialize total thermal resistance

                for layer in construction['layers']:
                    material_name = layer['material']
                    material = next((m for m in material_data['materials'] if m['name'] == material_name), None)
                    if material:
                        thickness = layer['thickness']
                        thermal_conductivity = material['thermal_conductivity']

                        # Calculate the resistance of the layer
                        resistance = thickness / thermal_conductivity
                        total_resistance += resistance

                        print(f"    Material: {material_name}")
                        print(f"      Thickness: {thickness} m")
                        print(f"      Thermal Conductivity: {thermal_conductivity} W/(m·K)")
                        print(f"      Resistance: {resistance:.4f} m²·K/W")
                    else:
                        print(f"    Material: {material_name} (No details found)")

                if total_resistance > 0:
                    # Calculate the U-value
                    u_value = 1 / total_resistance
                    print(f"  Total Resistance (R): {total_resistance:.4f} m²·K/W")
                    print(f"  U-value: {u_value:.4f} W/(m²·K)")
                else:
                    print("  Unable to calculate U-value (no valid layers).")





        return {'FINISHED'}
