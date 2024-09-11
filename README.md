# Automation tools for working with ground-based spectrometry retrievals

Python tools

creating a virtual environment with a specific version using conda (used mini conda).
`conda create -n mypython3.8 python=3.8`
This is useful because don't need to explicitly download different versions of python and em27-retrieval-pipeline requires python 3.11.*

Input files needed for PROFFASTpylot processing chain:

| `input_<instrument identifiers>.yml` config param | input file format | description |
| --- | --- | --- |
| coord_file | `.csv` | Column names: `Site, Latitude, Longitude, Altitude_kmasl, Starttime` Sodankylä values: `Sodankyla, 67.366, 26.630, 0.181, 2014-01-01`. Can include other sites as well.
| interferogram_path | | |
| map_path | folder containing `.map` files ||
| pressure_path | folder containing `.dat` files ||
| pressure_type_file | `.yml` ||