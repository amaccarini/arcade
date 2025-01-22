---
title: 'Arcade: An urban building energy modeling tool powered by AI for input data collection'
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

**Arcade** is a free and open-source UBEM tool developed as an add-on extension for Blender [@Blender]. Arcade leverages 3D visualization of building geometries and incorporates a reduced-order building thermal model for efficient energy simulations. It utilizes Blender’s Python  API to create custom panels and user interfaces, allowing seamless interaction directly within the Blender interface. Additionally, it features an AI-powered image recognition module to extract building attributes often unavailable in datasets, such as building height and construction age.

The primary purpose of Arcade is to generate hourly heating and cooling demand data for urban areas, supporting the design and optimization of district heating and cooling systems. Key features of Arcade include:

- **3D Visualization**: Seamless integration with Blender for 3D building visualization and parameter configuration.
- **Energy Simulation**: Calculation of hourly heating and cooling demand using a simplified resistance-capacitance thermal model.
- **Automatic building data enrichment**: Gaps in building attributes from OpenStreetMap datasets (i.e., height and construction age) automatically filled using either a user-defined probabilistic method or BRAILS, an AI-powered image recognition module.
- **Building archetypes**: A set of pre-defined archetypes covering four geographical locations (Denmark and three regions in the US), two occupancy types (Residential and Offices), and multiple construction age periods.

# Statement of need

`Gala` is an Astropy-affiliated Python package for galactic dynamics. Python
enables wrapping low-level languages (e.g., C) for speed without losing
flexibility or ease-of-use in the user-interface. The API for `Gala` was
designed to provide a class-based and user-friendly interface to fast (C or
Cython-optimized) implementations of common operations such as gravitational
potential and force evaluation, orbit integration, dynamical transformations,
and chaos indicators for nonlinear dynamics. `Gala` also relies heavily on and
interfaces well with the implementations of physical units and astronomical
coordinate systems in the `Astropy` package [@astropy] (`astropy.units` and
`astropy.coordinates`).

`Gala` was designed to be used by both astronomical researchers and by
students in courses on gravitational dynamics or astronomy. It has already been
used in a number of scientific publications [@Pearson:2017] and has also been
used in graduate courses on Galactic dynamics to, e.g., provide interactive
visualizations of textbook material [@Binney:2008]. The combination of speed,
design, and support for Astropy functionality in `Gala` will enable exciting
scientific explorations of forthcoming data releases from the *Gaia* mission
[@gaia] by students and experts alike.

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
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References
