# Arcade: a UBEM tool powered by AI

## Overview
**Arcade** is a free and open-source Urban Building Energy Modeling (UBEM) tool developed as a Python add-on extension for Blender. It leverages 3D visualization of building geometries and an AI-powered image recognition module to extract key building attributes that are often unavailable, such as building height and construction age. Arcade’s primary purpose is to generate hourly heating and cooling demand data of urban areas in just a few clicks, supporting the design and optimization of efficient district heating and cooling systems.

---

## Features
### Key Capabilities
- **3D Visualization**: Seamless integration with Blender for 3D visualization of buildings.
- **Energy Simulation**: Hourly heating and cooling demand calculation based on a simplified resistance-capacitor thermal model.
- **Automatic building data enrichment**: Missing building attributes (e.g., height and construction age) can be estimated using either a user-defined probabilistic method or an AI-powered image recognition module [BRAILS](https://nheri-simcenter.github.io/BRAILS-Documentation/index.html).
- **Building archetypes**: Arcade includes four building archetypes, each representing a distinct climatic region: Denmark, US-2A (Houston), US-3C (San Francisco), and US-5A (Chicago). Additional archetypes may be incorporated into Arcade in future updates.

---

## Installation
Arcade was designed with a simple installation process in mind, requiring no prior Python knowledge or manual installation of dependencies by the user. The tool is packaged as a Blender add-on extension, making the installation process extremely straightforward. To get started, you only need to download three items:

- **Blender**: Version 4.3 [Donwload Blender here](https://blender.org)
- **Arcade**: Latest release of Arcade as `.zip` file. Arcade is compatible with Windows (x86) and macOS (ARM64).
- **Weather data**: A `.epw` file representing the climate conditions of the area of interest. Such files can be downloaded from the [EnergyPlus website](https://energyplus.net/weather)

> ❗ **Important:** As outlined in the BRAILS documentation, a Google API key is required to successfully run the image recognition model. Instructions on obtaining a Google API key can be found [here](https://developers.google.com/maps/documentation/embed/get-api-key). BRAILS uses Maps Static API and Street View Static API to access satellite and street-level imagery. Ensure that both APIs are enabled when configuring your Google API key.
>

### Steps
Launch Blender and go to **Edit > Preferences > Get Extensions**. Next, click the dropdown arrow in the top-right corner of the window to expand the menu, then select **Install from Disk...**

![my_pref](images/pref.png)

Next, select the Arcade `.zip` file to enable the add-on. The installation process may take a few minutes as Blender installs the necessary Python packages. During this time, Blender may become unresponsive.

---

## Quickstart
### Settings
Before using Arcade, you need to configure a few settings in the Preferences panel. Navigate to **Edit > Preferences > Add-ons** and search for Arcade. Expand the Arcade panel to access its preferences.

First, specify an output folder (it’s recommended to choose a folder where you have write permissions). Next, select the weather file. If you plan to use BRAILS, you’ll also need to provide a Google API key as a string.

### Basic tutorial
Once Arcade is installed and the preferences are configured, you’re ready to get started! First, delete the three default objects created by Blender at startup to ensure a clean scene. Next, press `N` to open Blender’s Sidebar. You should now see the Arcade panel in the Sidebar. Click on it to explore the various sub-panels, buttons, and settings available in Arcade.

![my_menu](images/menu.png)

The workflow can be divided in three steps:
- **Generate the geoJSON file**: Start by pressing the `Create geoJSON file` button. This action prompts Arcade to generate a geoJSON file containing the building footprints of an urban area. The area is defined by a bounding box with four parameters: maximum latitude, maximum longitude, minimum latitude, and minimum longitude. By default, these parameters correspond to a small block in Berkeley, California.
- **Import the geoJSON file**: Next, select the generated geoJSON file by pressing the folder icon. You will find the geoJSON in the output folder that you chose in the Preferences panel. Once you click `Import geoJSON file`, Arcade will create the buildings in the Blender scene!
- **Run energy simulations**: Finally, select all buildings in the scene, and press the `Calculate Heating and Cooling Loads` button. Arcade will run energy simulations and output a `.csv` file with hourly heating and cooling loads for each building.

The full documentation of Arcade can be found [here](https://arcadedocs.readthedocs.io/en/latest/index.html).
