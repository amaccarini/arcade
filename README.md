# Arcade: a UBEM tool powered by AI

## Overview
**Arcade** is an Urban Building Energy Modeling (UBEM) tool developed as a Python add-on extension for Blender. It leverages 3D visualization of building geometries and an AI-powered image detection module to extract key building attributes that are often unavailable, such as building height and construction age. Arcade’s primary purpose is to generate hourly heating and cooling demand data for urban areas in just a few clicks, supporting the design and optimization of efficient district heating and cooling systems. 

---

## Features
### Key Capabilities
- **3D Visualization**: Seamless integration with Blender for 3D visualization of buildings.
- **Energy Simulation**: Hourly heating and cooling demand calculation based on a simplified resistance-capacitor (5R1C) method.
- **Automatic building data enrichment**: Missing building attributes (e.g., height and construction age) can be estimated using either a user-defined probabilistic method or an AI-powered image recognition module (BRAILS).
- **Building archetypes**: Arcade includes four building archetypes, each representing a distinct climatic region: Denmark, US-2A (Houston), US-3C (San Francisco), and US-5A (Chicago). Additional archetypes may be incorporated into Arcade in future updates.

---

## Installation
Arcade was designed with a simple installation process in mind, requiring no prior Python knowledge or manual installation of dependencies by the user. The tool is packaged as a Blender add-on extension, making the installation process extremely straightforward. To get started, you only need to download two items:

- **Blender**: Version 4.3 [Donwload Blender here](https://blender.org)
- **Arcade**: Latest release of Arcade as `.zip` file. Arcade is compatible with Windows (x86) and macOS (ARM64).

> 💡 **Note:** This is an informational note. It can be used to highlight important information or guidance.

### Steps
Launch Blender and enable the UBEM add-on via **Edit > Preferences > Add-ons**.
