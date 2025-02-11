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

With rapid urbanization, more than half of the global population now lives in cities, a trend expected to continue in the coming decades [@UN:2015]. Urban areas, while engines of economic growth and innovation, are also responsible for a significant share of global energy consumption and greenhouse gas emissions. Buildings, as key components of urban infrastructure, account for a substantial portion of this energy demand, driven by heating, cooling, lighting, and other operational needs.

In this context, Urban Building Energy Modeling (UBEM) has emerged as a powerful tool to analyze the energy use at the city scale. UBEM involves creating simulation-based models of building stocks, leveraging diverse datasets and computational tools to assess energy performance, evaluate retrofit strategies, and support sustainable urban planning.

**Arcade** is a free and open-source UBEM tool developed as an add-on extension for Blender [@Blender], a 3D computer graphics software. Arcade incorporates a reduced-order building thermal model for efficient energy simulations and uses Blender’s Python API to create custom panels and user interfaces. Additionally, it features an AI-powered image recognition module to extract building attributes often unavailable in datasets, such as building height and construction age.

Key features of Arcade include:

- **3D Visualization**: Seamless integration with Blender for 3D building visualization and parameter configuration.
- **Energy Simulation**: Calculation of hourly heating and cooling demand using a simplified resistance-capacitance thermal model.
- **Automatic building data enrichment**: Gaps in building attributes from OpenStreetMap (OSM) datasets are automatically filled using either a user-defined probabilistic method or BRAILS, an AI-powered image recognition module.
- **Building archetypes**: Predefined archetypes act as proxies for real buildings, enhancing scalability and computational efficiency by representing variations in location, occupancy, and construction age.

# Statement of need

In recent years, several UBEM tools have been developed to support the analysis and optimization of energy demand in urban areas [@UBEMreview1]. Despite these advancements, one of the major challenges remains the availability of reliable geospatial datasets, including key building attributes such as geometry, construction year, and occupancy type, among others. These datasets are essential, as they are converted into input parameters for the UBEM simulation engine after pre-processing and manipulation. Although governments worldwide are releasing more such datasets, these efforts are often fragmented [@Biljecki2021].
Therefore, researchers have increasingly relied on crowdsourced platforms such as OSM. These platforms provide free access to data and often offer better coverage than official sources. However, the quality and completeness can vary significantly between countries or even cities, thereby impacting the application of urban analytics [@Wang2025]. For instance, while the city of Berkeley has approximately 35,000 buildings mapped in OSM, only 1,500 include height-related information, and a handful of buildings have data about the construction year, which is particularly critical for categorizing buildings into archetypes for energy simulations.

In this context, Arcade differentiates itself from other UBEM tools by featuring a built-in functionality that leverages an AI-enabled module to automatically enrich incomplete OSM data using satellite and street-level imagery. Arcade is designed to be used by researchers, professionals, and students in the field of urban energy modeling and district thermal networks. The main simulation output consists of hourly data of heating and cooling demand of the urban area under investigation. This output data could be used for several further analysis such as:
- Retrofit scenario evaluation: Arcade can simulate and evaluate different retrofit scenarios to optimize energy performance, improve building efficiency, and reduce carbon emissions at the urban scale.
urban areas, supporting the design and optimization of district heating and cooling systems.23

# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](images/image_workflow.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References
