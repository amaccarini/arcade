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
- **Weather data**: A `.epw` file representing the climate conditions of the area of interest. Such files can be donwloaded from the [EnergyPlus website](https://energyplus.net/weather)

> ❗ **Important:** As outlined in the BRAILS documentation, a Google API key is required to successfully run the image recognition model. Instructions on obtaining a Google API key can be found [here](https://developers.google.com/maps/documentation/embed/get-api-key). BRAILS uses Maps Static API and Street View Static API to access satellite and street-level imagery. Ensure that both APIs are enabled when configuring your Google API key.
>

### Steps
Launch Blender and enable the Arcade add-on via **Edit > Preferences > Add-ons**.
