import json
import os

addon_directory = os.path.dirname(os.path.realpath(__file__))

def load_json(file_name):
    file_path = os.path.join(addon_directory, file_name)
    with open(file_path, 'r') as file:
        return json.load(file)

# Load the materials and constructions JSON data
materials_data = load_json('materials.json')
constructions_data = load_json('constructions.json')

# Create a material lookup dictionary for easy access
material_lookup = {m["name"]: m for m in materials_data["materials"]}

def calculate_uvalue_and_km(layers, h_tra, thickness_eff=None):
    """
    Calculate U-value for all layers and total km considering thickness_eff.
    thickness_eff: maximum thickness to consider for km (from indoor, first layers).
    """
    total_resistance = h_tra  # Initial resistance based on construction type
    total_km = 0  # Total km
    current_thickness = 0  # Track the cumulative thickness for km calculation

    # U-value: Always considers the full layer thickness
    for layer in layers:
        material_name = layer["material"]
        thickness = layer["thickness"]

        # Get material properties
        material = material_lookup.get(material_name)
        if not material:
            raise ValueError(f"Material '{material_name}' not found in materials data.")

        thermal_conductivity = material["thermal_conductivity"]

        # U-value calculation
        if thermal_conductivity > 0:
            total_resistance += thickness / thermal_conductivity

    # km: Limited by thickness_eff
    for layer in layers:
        material_name = layer["material"]
        thickness = layer["thickness"]

        # Get material properties
        material = material_lookup.get(material_name)
        specific_heat_capacity = material["specific_heat_capacity"]
        density = material["density"]

        # km calculation respecting thickness_eff
        if thickness_eff is None or current_thickness < thickness_eff:
            remaining_thickness = thickness_eff - current_thickness if thickness_eff else thickness
            effective_thickness = min(thickness, remaining_thickness)

            total_km += density * specific_heat_capacity * effective_thickness
            current_thickness += effective_thickness

            # Stop adding km once thickness_eff is reached
            if thickness_eff is not None and current_thickness >= thickness_eff:
                break

    # Final U-value calculation
    u_value = 1 / total_resistance if total_resistance > 0 else 0

    return round(u_value, 2), round(total_km, 2)

# Define prefixes, regions, and time periods
archetype_prefixes = ["RES_1", "COM_1"]  # Updated to include multiple prefixes
archetype_regions = ["DK", "US_2A", "US_3C", "US_5A"]
archetype_years_dk = ["1850", "1851_1930", "1931_1950", "1951_1960", "1961_1972", "1973_1978", "1979_1998", "1999_2006", "2007_2010", "2011"]
archetype_years_us = ["1980", "1980_2004", "2004"]

# Define h_tra values for each construction type
h_tra_values = {
    "floor": 0,
    "walls": 0,
    "roof": 0,
    "window": 0
}

# Generate archetypes
archetypes = []

for prefix in archetype_prefixes:  # Iterate over prefixes
    for region in archetype_regions:
        # Use different time periods based on region
        archetype_years = archetype_years_dk if region == "DK" else archetype_years_us

        for year in archetype_years:
            archetype_name = f"{prefix}_{year}_{region}"
            description = (
                f"{'Residential' if prefix == 'RES_1' else 'Commercial'} building "
                f"built in {year.replace('_', '-')} in {region}."
            )

            # Initialize the archetype entry
            archetype = {
                "name": archetype_name,
                "description": description,
                "constructions": {}
            }

            # Match constructions for floor, walls, roof, and window
            for part in ["Floor", "Walls", "Roof", "Window"]:
                part_key = part.lower()
                construction_name = f"{part}_{archetype_name}"
                matching_construction = next(
                    (c for c in constructions_data["constructions"] if c["name"] == construction_name), None
                )

                if matching_construction:
                    h_tra = h_tra_values[part_key]

                    # Special handling for windows to include g-factor and wwr
                    if part == "Window":
                        layers = matching_construction["layers"]
                        # Extract g-factor and wwr from the first layer
                        g_factor = layers[0].get("g-factor", None)
                        wwr = layers[0].get("wwr", None)
                        u_value, total_km = calculate_uvalue_and_km(layers, h_tra)

                        # Add window properties with g-factor and wwr
                        archetype["constructions"][part_key] = {
                            "Uvalue": u_value,
                            "k_m": total_km,
                            "g-factor": g_factor,
                            "wwr": wwr
                        }
                    else:
                        # Normal handling for floor, walls, and roof
                        u_value, total_km = calculate_uvalue_and_km(matching_construction["layers"], h_tra)
                        archetype["constructions"][part_key] = {
                            "Uvalue": u_value,
                            "k_m": total_km
                        }
                else:
                    archetype["constructions"][part_key] = "N/A"

            archetypes.append(archetype)

# Create the final JSON structure
output_data = {"archetypes": archetypes}

# Save the output to a new JSON file
addon_directory_out = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def save_json(output_data, file_name):
    """
    Saves the provided data to a JSON file in the add-on directory.

    Args:
        output_data (dict): The data to save to the JSON file.
        file_name (str): The name of the output JSON file.
    """
    file_path_out = os.path.join(addon_directory_out, file_name)
    with open(file_path_out, 'w') as file:  # Open in write mode
        json.dump(output_data, file, indent=4)
    print(f"JSON file saved to: {file_path_out}")

file_name = "archetypes.json"
save_json(output_data, file_name)
