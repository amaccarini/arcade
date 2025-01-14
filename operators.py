from .functions import latlon_to_xyz, create_flat_face, create_building, calculate_horizontal_area, calculate_and_group_vertical_faces, process_archetype, fetch_buildings_geojson, get_csv_column
import bpy
import json
import os
import math
from pvlib.iotools import read_epw
from pvlib import location, irradiance
import pandas as pd
import numpy as np
import webbrowser
from brails.modules import (YearBuiltClassifier, NFloorDetector,OccupancyClassifier)
from brails.workflow.FootprintHandler import FootprintHandler
from brails.workflow.ImHandler import ImageHandler
from mathutils import Vector
import geopandas as gpd

class ADDON1_OT_Operator(bpy.types.Operator):
    bl_idname = "generate.myop_operator"
    bl_label = "Create gejson file"

    def execute(self, context):
        props = context.scene.my_addon_props

        # If probabilistic option selected, start to create buildings using settings
        if props.tick_box_1:
            # Fetch bbox coordinates from properties
            bbox = (props.lat_min, props.lon_min, props.lat_max, props.lon_max)
            start_date_mean=props.avg_age
            start_date_std_dev=props.std_age
            levels_mean=props.avg_nfloor
            levels_std_dev=props.std_nfloor

            # Call the fetch function with the specified folder
            result = fetch_buildings_geojson(bbox, bpy.context.preferences.addons[__package__].preferences.folder_path, start_date_mean, start_date_std_dev, levels_mean, levels_std_dev)

            # Report the result
            if "saved" in result:
                self.report({'INFO'}, result)
                print("GeoJSON file generated successfully.")
            else:
                self.report({'ERROR'}, result)




        #If AI option selected, start to create buildings using BRAILS
        elif props.tick_box_2:

            # Change the working directory to avoid Blender to save tmp folder in restricted folders
            os.chdir(os.path.expanduser(bpy.context.preferences.addons[__package__].preferences.folder_path))

            NBLDGS = 'all'

            # Get footprint data for Alvito, Italy from OSM (can also set fpSource='ms'):
            fp_handler = FootprintHandler()
            fp_handler.fetch_footprint_data((props.lon_min,props.lat_min, props.lon_max, props.lat_max),
                                            fpSource='osm',
                                            lengthUnit='m')

            footprints = fp_handler.footprints
            if NBLDGS == 'all':
                NBLDGS = len(footprints)

            # Get street-level imagery for Alvito by using the footprint locations:
            image_handler = ImageHandler('AIzaSyBJoY6tFIBZHjthJqOqdJPi1XsFzoP5nLo')
            image_handler.GetGoogleStreetImage(fp_handler.footprints)
            imstreet = [im for im in image_handler.street_images if im is not None]

            # Initialize the era of construction classifier:
            year_model = YearBuiltClassifier()

            # Call the classifier to determine the era of construction for
            # each building:
            year_model.predict(imstreet)

            # Get the prediction results:
            preds = year_model.results_df.copy(deep=True)

            # Prepare preds for merging with building inventory:
            preds_era = preds.rename(
                columns={'prediction': 'YearBuilt',
                          'image': 'street_images'}).drop(
                              columns=['probability'])

            # Initialize the floor detector:
            nfloor_model = NFloorDetector()

            # Call the floor detector to determine number of floors of
            # buildings in each image:
            nfloor_model.predict(imstreet)

            # Get predictions and prepare them for merging with the building inventory:
            preds_nfloor = pd.DataFrame(
                list(zip(nfloor_model.system_dict['infer']['images'],
                          nfloor_model.system_dict['infer']['predictions'])),
                columns=['street_images', 'NumberOfStories'])

            # Initialize the occupancy classifier object:
            occupancy_model = OccupancyClassifier()

            # Call the occupancy classifier to determine the occupancy
            # class of each building:
            occupancy_model.predict(imstreet)

            # Write the prediction results to a DataFrame:
            preds_occ = pd.DataFrame(occupancy_model.preds, columns=[
                'street_images', 'OccupancyClass'])

            # Write prediction results into the inventory DataFrame:
            inventory_df = pd.DataFrame(
                pd.Series(fp_handler.footprints, name='Footprint'))
            inventory_df.Footprint = fp_handler.footprints
            lon = []
            lat = []
            for pt in fp_handler.centroids:
                lon.append(pt.x)
                lat.append(pt.y)
            inventory_df['Latitude'] = lat
            inventory_df['Longitude'] = lon
            inventory_df['PlanArea'] = fp_handler.attributes['fparea']

            inventory_df['street_images'] = image_handler.street_images
            inventory_df = inventory_df.merge(preds_era,
                                              how='left',
                                              on='street_images')
            inventory_df = inventory_df.merge(preds_nfloor,
                                              how='left',
                                              on='street_images')
            inventory_df['NumberOfStories'] = inventory_df['NumberOfStories'].astype(dtype='Int64')
            inventory_df = inventory_df.merge(preds_occ,
                                              how='left',
                                              on='street_images')

            # Convert inventory_df to a GeoJSON format with polygons and properties
            features = []
            for idx, row in inventory_df.iterrows():
                feature = {
                    "type": "Feature",
                    "properties": {
                        "id": idx + 1,
                        "Latitude": row['Latitude'],
                        "Longitude": row['Longitude'],
                        "start_date": str(row['YearBuilt']) if pd.notna(row['YearBuilt']) else "NA",
                        "building:levels": str(row['NumberOfStories']) if pd.notna(row['NumberOfStories']) else "NA",
                        "building": str(row['OccupancyClass']) if pd.notna(row['OccupancyClass']) else "NA",
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [[point[0], point[1]] for point in row['Footprint']]
                        ]
                    }
                }
                features.append(feature)

            geojson_data = {
                "type": "FeatureCollection",
                "features": features
            }

            # Save the GeoJSON file
            output_folder=bpy.context.preferences.addons[__package__].preferences.folder_path
            output_geojson = f"{output_folder}/enriched_buildings_ai.geojson"
            with open(output_geojson, "w") as f:
                import json
                json.dump(geojson_data, f, indent=2)

            print(f"GeoJSON file saved to: {output_geojson}")


        return {'FINISHED'}




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

        #-----Define basic climate and geographic info----------

        #read the .epw file
        epwFile = bpy.context.preferences.addons[__package__].preferences.file_path
        epw_data = read_epw(epwFile)

        #export timezone and convert it into string with sign changed
        tz_epw = int(epw_data[1]['TZ'])
        sign = '+' if tz_epw <= 0 else '-'
        timezone_string = f"Etc/GMT{sign}{abs(tz_epw)}"

        #define weather parameters for solar calculation
        lat=epw_data[1]['latitude']
        lon=epw_data[1]['longitude']
        ghi=epw_data[0]['ghi'].tz_localize(None).reset_index(drop=True)
        dni=epw_data[0]['dni'].tz_localize(None).reset_index(drop=True)
        dhi=epw_data[0]['dhi'].tz_localize(None).reset_index(drop=True)
        Text = epw_data[0].filter(['temp_air'])

        loc = location.Location(lat,lon)
        times = pd.date_range(start='01-01-2021', end='12-31-2021 23:00', freq='h', tz=timezone_string)
        sp = loc.get_solarposition(times)

        solar_zenith=sp['apparent_zenith'].reset_index(drop=True)
        solar_azimuth=sp['azimuth'].reset_index(drop=True)


        #--------START LOOP FOR BUILDINGS----------------------
        all_buildings_data = {}  # For hourly loads
        all_buildings_parameters = {}  # For building parameters

        for cube in selected_objects:

            #Calculate number of floors, ensuring that the value is minimum = 1
            num_floors = max(1, math.floor(cube.dimensions.z / 3))

            #Calculate the horizontal area of the building, and then floor area and roof area
            horizontal_face_area=calculate_horizontal_area(cube, threshold=0.01)
            Aflo_tot=horizontal_face_area*num_floors
            Aflo=horizontal_face_area
            Aroo=horizontal_face_area

            #Calculate the vertical areas of the building together with their orientation
            vertical_faces_areas=calculate_and_group_vertical_faces(cube, threshold=0.01, angle_tolerance=30)

            #Calculate total sum of vertical areas, and then area of walls (opaque) and windows
            tot_vertical_area=sum(vertical_faces_areas.values())

            #Select the archetype
            archetype_country=context.scene.my_addon_props.bui_arch

            #Process the archetypes JSON file to match the archetype
            process_archetype(cube, archetype_data, archetype_country)

            constructions_data=process_archetype(cube, archetype_data, archetype_country)


            Awal=tot_vertical_area*(1-constructions_data.get("window")["wwr"]) #float
            Awin=tot_vertical_area*(constructions_data.get("window")["wwr"]) #float
            Awal_list=[x * (1-constructions_data.get("window")["wwr"]) for x in list(vertical_faces_areas.values())] #list
            Awin_list=[x * (constructions_data.get("window")["wwr"]) for x in list(vertical_faces_areas.values())] #list

            #Calculate the total heat capacity of the building (1C) (windows are not involved - Eq. 66)
            Cm_floor=constructions_data.get("floor")["k_m"]*Aflo_tot
            Cm_roof=constructions_data.get("roof")["k_m"]*Aroo
            Cm_walls=constructions_data.get("walls")["k_m"]*Awal
            Cm_tot=Cm_floor+Cm_roof+Cm_walls

            #Calculate the effective mass area Am - Eq. 65)
            den_floor=constructions_data.get("floor")["k_m"]**2*Aflo_tot
            den_roof=constructions_data.get("roof")["k_m"]**2*Aroo
            den_walls=constructions_data.get("walls")["k_m"]**2*Awal
            Am=Cm_tot**2/(den_floor+den_roof+den_walls)

            #Calculate the volume of the building
            vol=horizontal_face_area*cube.dimensions.z


            #---------------Definition of constant parameters---------------------- MAYBE TO MOVE BEFORE LOOP as they are constant

            #Adjustment factor for floor
            b=0.5

            #Heat transfer coefficient between surface and air nodes
            h_sa=3.45 #W/m2K

            #Heat trannsfer coefficient between mass and surface nodes
            h_ms=9.1 #W/m2K

            #Ratio between internal surfaces and floor area (dimensionless)
            ratSur=4.5

            #Absorption coefficient for solar radiation (dimensionless)
            absCoe=0.6

            #Heat resistance of external surfaces
            surRes=0.04 #m2K/W

            #Emissivity of external surfaces (dimensionless)
            eps=0.9

            #Air change rate (MAYBE TO BE MOVED INSIDE ARCHETYPES JSON FILE AS IT IS ARCHETYPE-SPECIFIC)
            ACH=0.15

            #--------------Calculation of heat transfer elements (5R) -----------------------

            Atot=Aflo_tot*ratSur

            #Heat transfer element for ventilation (Eq. 21)
            Hven=1.225*1005*ACH*vol/3600

            #Heat transfer element for windows (Eq. 17)
            Hwin=constructions_data.get("window")["Uvalue"]*Awin

            #Heat transfer element for opaque surfaces (Eq. 63)
            Uwal=constructions_data.get("walls")["Uvalue"]
            Uflo=constructions_data.get("floor")["Uvalue"]
            Uroo=constructions_data.get("roof")["Uvalue"]
            Hem=1/(1/(Uwal*Awal+b*Uflo*Aflo+Uroo*Aroo)-1/(h_ms*Am))

            #Heat transfer element between mass and surface node
            Htr_ms=h_ms*Am

            #Heat transfer element between surface and air node
            Htr_sa=h_sa*Atot

            #---------CALCULATE SOLAR RADIATION ON SURFACES-----------


            #---Calculate solar radiation on vertical surfaces
            POA_irradiance_values = []


            # Iterate over each azimuth angle stored in vertical_faces_areas.keys
            for azimuth_angle in vertical_faces_areas.keys():
                # Calculate POA irradiance for the current azimuth angle
                POA_irradiance = irradiance.get_total_irradiance(surface_tilt=90, surface_azimuth=azimuth_angle,
                                                     solar_zenith=solar_zenith, solar_azimuth=solar_azimuth,
                                                     dni=dni, ghi=ghi, dhi=dhi)
                POA_global=POA_irradiance['poa_global']
                # Append the POA irradiance value to the list
                POA_irradiance_values.append(POA_global)

            POA_irradiance_values_df=pd.DataFrame(POA_irradiance_values)

            #---Calculate solar radiation through windows
            multiplied_values_win = []

            # Iterate over values in Awin and corresponding POA_irradiance_values
            for win_value, poa_value in zip(Awin_list, POA_irradiance_values):
                # Multiply the values and append the result to the list
                multiplied_value_win = win_value * poa_value*constructions_data.get("window")["g-factor"]
                multiplied_values_win.append(multiplied_value_win)

            multiplied_values_win_df=pd.DataFrame(multiplied_values_win)
            solRadWin_tot=sum(multiplied_values_win)

            #---Calculate solar radiation through opaque constructions
            multiplied_values_opa = []

            #Calculate for the vertical walls
            # Iterate over values in Awal_list and corresponding POA_irradiance_values
            for opa_value, poa_value in zip(Awal_list, POA_irradiance_values):
                # Multiply the values and append the result to the list
                multiplied_value_opa = opa_value * poa_value*absCoe*Uwal*surRes
                multiplied_values_opa.append(multiplied_value_opa)

            multiplied_values_opa_df=pd.DataFrame(multiplied_values_opa)

            multiplied_values_t_opa = []

            for areaWal in Awal_list:
                multiplied_value_t_opa=areaWal*Uwal*surRes*5*eps*11*0.5
                multiplied_values_t_opa.append(multiplied_value_t_opa)

            multiplied_values_t_opa_df=pd.DataFrame(multiplied_values_t_opa)

            #Total solar radiation on opaque vertical surface
            solRadOpa_walls = [a - b for a, b in zip(multiplied_values_opa, multiplied_values_t_opa)]
            solRadOpa_walls_tot=sum(solRadOpa_walls)

            #Calculate for the roof
            POA_irradiance_roof = irradiance.get_total_irradiance(surface_tilt=0, surface_azimuth=0,
                                                 solar_zenith=solar_zenith, solar_azimuth=solar_azimuth,
                                                 dni=dni, ghi=ghi, dhi=dhi)
            POA_global_roof=POA_irradiance_roof['poa_global']

            multiplied_values_roo = POA_global_roof*Aroo*absCoe*Uroo*surRes

            multiplied_value_roo_t=Aroo*Uroo*surRes*5*eps*11*1
            multiplied_value_roo_t = [multiplied_value_roo_t] * len(multiplied_values_roo)

            #Total solar radiation on opaque vertical surface
            solRadOpa_roo_tot = [a - b for a, b in zip(multiplied_values_roo, multiplied_value_roo_t)]
            solRadOpa_roo_tot_df=pd.DataFrame(solRadOpa_roo_tot)

            #Sum solar radiation walls+roof
            solRadOpa = [a + b for a, b in zip(solRadOpa_walls_tot, solRadOpa_roo_tot)]
            solRadOpa_df = pd.Series(solRadOpa)

            #Calculate total solar radiation as sum of windows+opaque
            solRadTot = [a + b for a, b in zip(solRadOpa_df, solRadWin_tot)]
            solRadTot_df = pd.Series(solRadTot)


            #------------INTERNAL GAINS---------------------------

            #Set addon directory
            addon_dir = os.path.dirname(os.path.realpath(__file__))

            if cube.my_properties.usage=="RES_1":
                m2_person_RES=35 #m2 per person
                q_person=120 #heat load from occupants per person
                q_light_RES=3.88 #heat load from lighting per m2
                q_equip_RES=5.38 #heat load from equipment per m2

                csv_path = os.path.join(addon_dir, "utilities", "RES_SCH.csv")

                fraction_OCC=get_csv_column(csv_path, "RES_OCC_SCH")
                fraction_LGT=get_csv_column(csv_path, "RES_LIGHT_SCH")
                fraction_EQP=get_csv_column(csv_path, "RES_EQP_SCH")

                gain_OCC=[x * q_person * Aflo_tot / m2_person_RES for x in fraction_OCC]
                gain_LGT=[x * q_light_RES * Aflo_tot for x in fraction_LGT]
                gain_EQP=[x * q_equip_RES * Aflo_tot for x in fraction_EQP]

            else:
                m2_person_COM=18
                q_person=120
                q_light_COM=10.76
                q_equip_COM=10.76

                csv_path = os.path.join(addon_dir, "utilities", "COM_SCH.csv")

                fraction_OCC=get_csv_column(csv_path, "COM_OCC_SCH")
                fraction_LGT=get_csv_column(csv_path, "COM_LIGHT_SCH")
                fraction_EQP=get_csv_column(csv_path, "COM_EQP_SCH")

                gain_OCC=[x * q_person * Aflo_tot / m2_person_RES for x in fraction_OCC]
                gain_LGT=[x * q_light_RES * Aflo_tot for x in fraction_LGT]
                gain_EQP=[x * q_equip_RES * Aflo_tot for x in fraction_EQP]

            gain=[a + b + c for a, b, c in zip(gain_OCC, gain_LGT, gain_EQP)]
            gain_df=pd.Series(gain)


            #------------CALCULATIONS FOR HEAT INJECTIONS-------------------------------------
            phi_air=gain_df*0.5

            phi_sur=(1-Am/Atot-Hwin/(Atot*h_ms))*(0.5*gain_df+solRadTot_df)

            phi_mas=(Am/Atot)*(0.5*gain_df+solRadTot_df)

            #------------CALCULATION OF HEATING AND COOLING LOADS----------------------------

            a=[]
            c=[]
            Tm_ini=20
            Ti_set_hea=20
            Ti_set_coo=27


            for h in range(0, 8760, 1):

                A = np.array([[Hven+Htr_sa, -Htr_sa, 0], [Htr_sa, -Hwin-Htr_sa-Htr_ms, Htr_ms], [0, Htr_ms, -Hem-Htr_ms-Cm_tot/3600]])
                #b = np.array([phi_air+Hven*Tsup, -phi_sur-Hwin*Text.temp_air[h], -phi_mas-Cm_tot/3600*Tm_ini-Hem*Text.temp_air[h]])
                b = np.array([phi_air.iloc[h]+Hven*Text.temp_air.iloc[h], -phi_sur.iloc[h]-Hwin*Text.temp_air.iloc[h], -phi_mas.iloc[h]-Cm_tot/3600*Tm_ini-Hem*Text.temp_air.iloc[h]])
                x = np.linalg.solve(A, b)


                if x[0]<Ti_set_hea:
                    #Heating condition
                    A = np.array([[1, Htr_sa, 0], [0, -Hwin-Htr_sa-Htr_ms, Htr_ms], [0, Htr_ms, -Hem-Htr_ms-Cm_tot/3600]])
                    b = np.array([-Hven*Text.temp_air.iloc[h]+Hven*Ti_set_hea+Htr_sa*Ti_set_hea-phi_air.iloc[h], -phi_sur.iloc[h]-Hwin*Text.temp_air.iloc[h]-Ti_set_hea*Htr_sa, -phi_mas.iloc[h]-Cm_tot/3600*Tm_ini-Hem*Text.temp_air.iloc[h]])
                    x = np.linalg.solve(A, b)
                    a.append(Ti_set_hea)
                    c.append(x[0])
                    Tm_ini=x[2]

                elif x[0]>Ti_set_coo:

                    #Cooling condition
                    A = np.array([[1, Htr_sa, 0], [0, -Hwin-Htr_sa-Htr_ms, Htr_ms], [0, Htr_ms, -Hem-Htr_ms-Cm_tot/3600]])
                    b = np.array([-Hven*Text.temp_air.iloc[h]+Hven*Ti_set_coo+Htr_sa*Ti_set_coo-phi_air.iloc[h], -phi_sur.iloc[h]-Hwin*Text.temp_air.iloc[h]-Ti_set_coo*Htr_sa, -phi_mas.iloc[h]-Cm_tot/3600*Tm_ini-Hem*Text.temp_air.iloc[h]])
                    x = np.linalg.solve(A, b)
                    a.append(Ti_set_coo)
                    c.append(x[0])
                    Tm_ini=x[2]

                else:
                    #No heating and cooling needed
                    a.append(x[0])
                    c.append(0)
                    Tm_ini=x[2]

            # Postprocess `c` to set cooling load to 0 when Text < Ti_set_coo - 3
            for h in range(8760):
                if Text.temp_air.iloc[h] < (Ti_set_coo - 3) and c[h] < 0:
                    c[h] = 0  # Override cooling/heating load

            print(f"Calculation for {cube.name} completed")

            c = [round(value) for value in c]
            all_buildings_data[cube.name] = c

            # Store the parameters as a list in the parameters dictionary
            all_buildings_parameters[cube.name] = [round(Aflo_tot, 1), round(Cm_tot, 0), round(Uflo, 2)]



        # Add the "Hour of Year" as the first column in the hourly loads dictionary
        hour_of_year = list(range(1, 8761))  # Generate a list from 1 to 8760
        all_buildings_data["Hour of Year"] = hour_of_year

        # Create DataFrames for hourly loads and parameters
        df_all_buildings = pd.DataFrame(all_buildings_data)

        # Create the parameters DataFrame (transpose the dictionary)
        parameters_df = pd.DataFrame(all_buildings_parameters, index=["Floor area", "Capacity", "U-value"]).T

        # Save the hourly loads to a CSV file
        out_dir = bpy.context.preferences.addons[__package__].preferences.folder_path
        os.makedirs(out_dir, exist_ok=True)
        output_file_loads = os.path.join(out_dir, "All_Buildings_Loads_with_Hours.csv")
        df_all_buildings.to_csv(output_file_loads, sep=';', index=False)

        # Save the building parameters to a CSV file
        output_file_parameters = os.path.join(out_dir, "All_Buildings_Parameters.csv")
        parameters_df.to_csv(output_file_parameters, sep=';', index_label="Building")

        print(f"All building data (with hour of year) saved to: {output_file_loads}")
        print(f"Building parameters saved to: {output_file_parameters}")

        return {'FINISHED'}



class ADDON3_OT_Operator(bpy.types.Operator):
    bl_idname = "myaddon.open_browser"
    bl_label = "Open Website"
    bl_description = "Open the OSM website in your browser to easily define the latitude and longitude of your desired urban area."

    def execute(self, context):
        # URL to open
        url = "https://www.openstreetmap.org/export#map=4/49.07/17.84"
        webbrowser.open(url)
        return {'FINISHED'}


class ADDON4_OT_Operator(bpy.types.Operator):
    bl_idname = "file.open_file"
    bl_label = "Browse File"

    def execute(self, context):
        context.scene.filepath_props.file_path = self.filepath
        print(f"Selected File: {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ADDON5_OT_Operator(bpy.types.Operator):
    bl_idname = "import.open_file"
    bl_label = "Import file"
    bl_description = "Import the geoJSON file to create the 3D urban area"

    def execute(self, context):
        # Access the file path from the UI property
        file_path = context.scene.my_addon_props.file_path

        with open(file_path, 'r') as f:
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
            num_stories = feature['properties'].get('building:levels', "NA")
            year = feature['properties'].get('start_date', "NA")
            use = feature['properties'].get('building', "NA")

            # Get the @id property
            feature_id = feature.get('id', "Unnamed")
            # Replace "/" with "_" in the feature ID
            feature_id = str(feature_id).replace('/', '_')

            # Convert lat/lon to Blender coordinates, using the smallest lat/lon as the origin
            vertices = [latlon_to_xyz(lat, lon, min_lat, min_lon) for lon, lat in coordinates]

            # Calculate the horizontal footprint area
            obj_name = f"Temp_{feature_id}"  # Temporary name for footprint object
            temp_mesh = bpy.data.meshes.new(obj_name)
            temp_mesh.from_pydata([Vector((v[0], v[1], 0)) for v in vertices], [], [[i for i in range(len(vertices))]])
            temp_obj = bpy.data.objects.new(obj_name, temp_mesh)
            bpy.context.collection.objects.link(temp_obj)

            # Apply transformation and calculate the area
            footprint_area = calculate_horizontal_area(temp_obj)

            # Delete the temporary object after calculation
            bpy.data.objects.remove(temp_obj, do_unlink=True)

            # Check footprint area threshold
            if footprint_area*2 < 75:
                print(f"Skipping building {feature_id}: Footprint area ({footprint_area:.2f} m²) is less than 50 m².")
                continue

            # If height is "NA" or not defined, create a flat face
            if num_stories == "NA" or not num_stories.isdigit():
                create_flat_face(vertices, f"Flat_{feature['properties']['id']}")
            else:
                # Otherwise, create a building with the given height
                num_stories = float(num_stories)  # Convert height to float
                year = int(year)  # Convert year to int
                create_building(vertices, num_stories*3, f"Building_{feature_id}", year, use)

        print("Buildings created successfully.")

        return {'FINISHED'}
