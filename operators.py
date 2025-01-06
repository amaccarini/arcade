from .functions import latlon_to_xyz, create_flat_face, create_building, calculate_horizontal_area, calculate_and_group_vertical_faces, process_archetype, fetch_buildings_geojson
import bpy
import json
import os
import math
from pvlib.iotools import read_epw
from pvlib import location, irradiance
import pandas as pd
import numpy as np
import webbrowser
import brails
from mathutils import Vector

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
            print("2: Option 2 is selected")




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
        print(epw_data)

        #export timezone and convert it into string with sign changed
        tz_epw = int(epw_data[1]['TZ'])
        #print('ciao')
        #print(tz_epw)
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
        print(times)
        #print(sp)

        solar_zenith=sp['apparent_zenith'].reset_index(drop=True)
        solar_azimuth=sp['azimuth'].reset_index(drop=True)
        #print(solar_azimuth)

        #--------START LOOP FOR BUILDINGS----------------------

        for cube in selected_objects:

            #Calculate number of floors, ensuring that the value is minimum = 1
            num_floors = max(1, math.floor(cube.dimensions.z / 3))
            print(f"The nu_flors is {num_floors}")

            #Calculate the horizontal area of the building, and then floor area and roof area
            horizontal_face_area=calculate_horizontal_area(cube, threshold=0.01)
            Aflo_tot=horizontal_face_area*num_floors
            Aflo=horizontal_face_area
            Aroo=horizontal_face_area

            #Calculate the vertical areas of the building together with their orientation
            vertical_faces_areas=calculate_and_group_vertical_faces(cube, threshold=0.01, angle_tolerance=30)
            #print(vertical_faces_areas)
            print(type(vertical_faces_areas))
            #Calculate total sum of vertical areas, and then area of walls (opaque) and windows
            tot_vertical_area=sum(vertical_faces_areas.values())

            #Process the archetypes JSON file to match the archetype
            process_archetype(cube, archetype_data)

            #print(cube.my_properties.usage)
            #print(cube.my_properties.age)
            constructions_data=process_archetype(cube, archetype_data)
            #print(constructions_data)

            Awal=tot_vertical_area*(1-constructions_data.get("window")["wwr"]) #float
            Awin=tot_vertical_area*(constructions_data.get("window")["wwr"]) #float
            Awal_list=[x * (1-constructions_data.get("window")["wwr"]) for x in list(vertical_faces_areas.values())] #list
            Awin_list=[x * (constructions_data.get("window")["wwr"]) for x in list(vertical_faces_areas.values())] #list
            print('CIAOOOOOO')
            print(Awal_list)
            print(Awal)


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

            print(horizontal_face_area)
            print(Cm_floor)
            print(Cm_roof)
            print(Cm_walls)
            print(den_floor)
            print(f"The Am is {Am}")

            #Calculate the volume of the building
            vol=horizontal_face_area*cube.dimensions.z
            print(vol)

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

            #Internal heat gains
            gain=200

            #--------------Calculation of heat transfer elements (5R) -----------------------

            Atot=Aflo_tot*ratSur
            print(f"The Atot is {Atot}")

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


            #------------CALCULATIONS FOR HEAT INJECTIONS-------------------------------------
            phi_air=gain*0.5
            phi_sur=(1-Am/Atot-Hwin/(Atot*h_ms))*(0.5*gain+solRadTot_df)
            phi_mas=(Am/Atot)*(0.5*gain+solRadTot_df)

            #------------CALCULATION OF HEATING AND COOLING LOADS----------------------------

            a=[]
            c=[]
            Tm_ini=20
            Ti_set_hea=20
            Ti_set_coo=27


            for h in range(0, 8760, 1):

                A = np.array([[Hven+Htr_sa, -Htr_sa, 0], [Htr_sa, -Hwin-Htr_sa-Htr_ms, Htr_ms], [0, Htr_ms, -Hem-Htr_ms-Cm_tot/3600]])
                #b = np.array([phi_air+Hven*Tsup, -phi_sur-Hwin*Text.temp_air[h], -phi_mas-Cm_tot/3600*Tm_ini-Hem*Text.temp_air[h]])
                b = np.array([phi_air+Hven*Text.temp_air.iloc[h], -phi_sur.iloc[h]-Hwin*Text.temp_air.iloc[h], -phi_mas.iloc[h]-Cm_tot/3600*Tm_ini-Hem*Text.temp_air.iloc[h]])
                x = np.linalg.solve(A, b)


                if x[0]<Ti_set_hea:
                    A = np.array([[1, Htr_sa, 0], [0, -Hwin-Htr_sa-Htr_ms, Htr_ms], [0, Htr_ms, -Hem-Htr_ms-Cm_tot/3600]])
                    b = np.array([-Hven*Text.temp_air.iloc[h]+Hven*Ti_set_hea+Htr_sa*Ti_set_hea-phi_air, -phi_sur.iloc[h]-Hwin*Text.temp_air.iloc[h]-Ti_set_hea*Htr_sa, -phi_mas.iloc[h]-Cm_tot/3600*Tm_ini-Hem*Text.temp_air.iloc[h]])
                    x = np.linalg.solve(A, b)
                    a.append(Ti_set_hea)
                    c.append(x[0])
                    Tm_ini=x[2]

                elif x[0]>Ti_set_coo:
                    A = np.array([[1, Htr_sa, 0], [0, -Hwin-Htr_sa-Htr_ms, Htr_ms], [0, Htr_ms, -Hem-Htr_ms-Cm_tot/3600]])
                    b = np.array([-Hven*Text.temp_air.iloc[h]+Hven*Ti_set_coo+Htr_sa*Ti_set_coo-phi_air, -phi_sur.iloc[h]-Hwin*Text.temp_air.iloc[h]-Ti_set_coo*Htr_sa, -phi_mas.iloc[h]-Cm_tot/3600*Tm_ini-Hem*Text.temp_air.iloc[h]])
                    x = np.linalg.solve(A, b)
                    a.append(Ti_set_coo)
                    c.append(x[0])
                    Tm_ini=x[2]

                else:
                    a.append(x[0])
                    c.append(0)
                    Tm_ini=x[2]

            df = pd.DataFrame (a)
            df1=pd.DataFrame(c)
            fileName = cube.name
            out_dir = bpy.context.preferences.addons[__package__].preferences.folder_path
            os.makedirs(out_dir, exist_ok=True)

            # Combine directory and file name
            out_file = os.path.join(out_dir, fileName)

            df.to_csv(out_file + 'Temp' + '.csv', sep=';')
            df1.to_csv(out_file + 'Loads' + '.csv', sep=';')
            print(f"Calculation for {cube.name} completed")

            # Open the file in write mode
            # Specify the output file path
            #output_file = "/Users/alm/Documents/output_transposed.csv"

            # Transpose the DataFrame
            #transposed_df = POA_irradiance_values_df.T

            # Export the transposed DataFrame to a CSV file
            #transposed_df.to_csv(output_file, index=False)


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

        # Load the JSON file
        #folder_path = bpy.context.preferences.addons[__package__].preferences.folder_path

        # Define the file name
        #file_name = "enriched_buildings.geojson"
        #json_path = os.path.join(folder_path, file_name)

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
