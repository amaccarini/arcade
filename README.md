# Arcade: a UBEM tool powered by AI

## Overview
**Arcade** is an Urban Building Energy Modeling (UBEM) tool developed as a Python add-on extension for Blender. It leverages 3D visualization of building geometries and an AI-powered image detection module to extract key building attributes that are often unavailable, such as building height and construction age. Arcade’s primary purpose is to generate hourly heating and cooling demand data for urban areas, supporting the design and optimization of efficient district heating and cooling systems. 

---

## Features
### Key Capabilities
- **3D Visualization**: Seamless integration with Blender for 3D visualization of buildings.
- **Energy Simulation**: Hourly heating and cooling demand calculation based on a simplified resistance-capacitor (5R1C) method.
- **Automatic building data enrichment**: Missing building attributes (e.g., height and construction age) can be estimated using either a user-defined probabilistic method or an AI-powered image recognition module (BRAILS).
- **Building archetypes**: Four building archetypes are included in arcade, represeting four climatic regions: Denmark, US-2A (Houston), US-3C (San Francisco), US-5A (Chicago). Additional archetypes may be added to Arcade in the future. 

---

## Installation
Arcade was designed with a simple installation process in mind, requiring no prior Python knowledge or manual installation of dependencies by the user. The tool is packaged as a Blender add-on extension, making the installation process extremely straightforward. To get started, you only need to download two items:

- **Blender**: Version 4.3 [Link Text](https://blender.org)



### Steps
Launch Blender and enable the UBEM add-on via **Edit > Preferences > Add-ons**.
