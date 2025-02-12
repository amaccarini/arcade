---
title: 'Arcade: An urban building energy modeling tool powered by AI for input data enrichment'
tags:
  - Python
  - urban
  - dynamics
  - Blender
  - energy
authors:
  - name: Alessandro Maccarini
    orcid: 0000-0003-1434-3023
    #equal-contrib: true
    affiliation: "1" # (Multiple affiliations must be quoted)
affiliations:
 - name: Department of the Built Environment, Aalborg University, Denmark
   index: 1
date: 21 January 20125
bibliography: paper.bib

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
#aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
#aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

With rapid urbanization, more than half of the global population now lives in cities, a trend expected to continue in the coming decades [@UN:2015]. Urban areas, while engines of economic growth and innovation, are also responsible for a significant share of global energy consumption and greenhouse gas emissions. Buildings, as key components of urban infrastructure, account for a substantial portion of this energy demand, driven by heating, cooling, and other operational needs [@GONZALEZ2022].

In this context, Urban Building Energy Modeling (UBEM) has emerged as a powerful tool to analyze the energy use at the city scale [@SALVALAI2024]. UBEM involves creating simulation-based models of building stocks, leveraging diverse datasets and computational tools to assess energy performance, evaluate retrofit strategies, and support sustainable urban planning.

`Arcade` is a free and open-source UBEM tool developed as an add-on extension for Blender [@Blender], a 3D computer graphics software. `Arcade` incorporates a reduced-order building thermal model for efficient energy simulations and uses Blender’s Python API to enable custom panels and user interfaces. Additionally, it features an AI-powered image recognition module to extract building attributes often missing from geospatial datasets, such as building height and construction age.

Key features of `Arcade` include:

- **3D Visualization**: Seamless integration with Blender for 3D building visualization and parameter configuration.
- **Energy Simulation**: Calculation of hourly heating and cooling demand using a simplified resistance-capacitance thermal model.
- **Automatic building data enrichment**: Gaps in building attributes from OpenStreetMap (OSM) datasets are automatically filled using either a user-defined probabilistic method or BRAILS, an AI-powered image recognition module [@CETINER2024].
- **Building archetypes**: Predefined archetypes act as proxies for real buildings, enhancing scalability and computational efficiency by representing variations in location, occupancy, and construction age.



# Statement of need

In recent years, several UBEM tools have been developed to support the analysis and optimization of energy demand in urban areas [@UBEMreview1; @FERRANDO2020]. Despite these advancements, one of the major challenges remains the availability of reliable geospatial datasets, including key building attributes such as geometry, construction year, and occupancy type, among others. These datasets are essential, as they are converted into input parameters for the UBEM simulation engine after pre-processing and manipulation. Although governments worldwide are releasing more such datasets, these efforts are often fragmented [@Biljecki2021].
Therefore, researchers have increasingly relied on crowdsourced platforms such as OSM. These platforms provide free access to data and often offer better coverage than official sources. However, the quality and completeness can vary significantly between countries or even cities, thereby impacting the application of urban analytics [@Wang2025]. For instance, while the city of Berkeley has approximately 35,000 buildings mapped in OSM, only 1,500 include height-related information, and a handful of buildings have data about the construction year, which is particularly critical for categorizing buildings into archetypes for energy simulations.

In this context, `Arcade` differentiates itself from other UBEM tools by featuring a built-in functionality that leverages an AI-enabled module to automatically enrich incomplete OSM data using satellite and street-level imagery. `Arcade` is designed for researchers, professionals, and students working in the fields of urban energy modeling and district thermal networks. The main simulation output consists of hourly data of heating and cooling demand of the urban area under investigation. This output data can be used for various analyses, including urban planning, retrofit scenario evaluation, and the design and optimization of district heating and cooling systems.
The overall workflow of `Arcade` is illustrated in \autoref{fig:flowchart}.

![Arcade workflow.\label{fig:flowchart}](images/workflow3.png)


# Acknowledgements

Support from Barbaros Cetiner in the use of BRAILS is gratefully acknowledged.

# References
