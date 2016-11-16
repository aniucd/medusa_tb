# MEDUSA Toolbox
=========================

This code provides a common interface in order to download [Sentinel 1 and 2](https://sentinel.esa.int/web/sentinel/home) data using [Google Earth Engine](https://earthengine.google.com/) or [PEPS](https://peps.cnes.fr/rocket/#/home) portal.
It is developed in the [MEDUSA project](http://w3.onera.fr/medusa/) at [ONERA](http://www.onera.fr).

The code for PEPS is based on

## MEDUSA project
The *Multidate Earth observation Datamass for Urban Sprawl Aftercase* (MEDUSA) project is designed to bring together and promote processing of remote sensing images in the current context of big data, with a focus on developing a demonstrator

The project website is hosted at http://w3.onera.fr/medusa/.

## What for ?

Google Earth Engine and PEPS platforms allow to download the Sentinel products.
This code is not dedicated at massive worldwide downloads, it can be useful for small experiments on limited areas.
It may be the first step, to use algorithms or test functionalities not yet available on the two source platforms.

For wide area computation, using Google Earth Engine web or python interface and server computation would be indicated.
Examples are provided at https://developers.google.com/earth-engine/tutorial_api_01.


## Run a first example

To get in touch with the library, run the first example in a terminal:
```
python satellite.py -c path_to_examples/config_S1_ee.json
```

## Documentation

[Google Earth Engine](doc/ee.md)

[PEPS](doc/peps.md)
