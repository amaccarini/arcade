Data enrichment
=====

Arcade includes two methods for data enrichment during the creating of the geoJSON file:

- **Probabilistic**: When this method is selected (default) a sub-panel called ``Settings for Proabilistic method`` will appear. This method uses a `normal distribution <https://en.wikipedia.org/wiki/Normal_distribution>`_ approach to estimate the construction age and the number of stories of each building. For each of these two attributes, you need to specify the average value and the standard deviation. A smaller standard deviation indicates less variation around the average value, whereas a larger standard deviation allows for greater variability.


- **AI-enabled**: This method activates the Python BRAILS module to estimates the construction age and the number of stories of each buildings. BRAILS utilize deep learning (DL), and computer vision (CV) techniques to extract information from satellite and street level images. 

.. warning::

   The AI-enabled method may result in longer computation times, depending on your machine’s GPU settings. We recommend testing your machine’s performance by selecting small urban blocks with a maximum of 10-20 buildings.
