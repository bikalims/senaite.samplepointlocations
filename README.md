## senaite.samplepointlocations

`senaite.samplepointlocations` extends **Senaite** (the modern core of Bika LIMS) with 

### Features

In some use cases it makes sense to group a number of Sample Points together on their Location, e.g. a number of water Sample Points per village or building complex or lubrication points on a big piece of machinery

Install the Bika add-on senaite.samplepointlocations for this two tier Sample Point addressing to be available

Sample Point Locations* then replaces Sample Points in the UI, and Sample Points are configured 'inside' Locations

Since the Location term is already used for Sample Storage Locations and for Instruments too, the locations here are called Sample Point Locations

### Documentation

Full documentation for end users can be found in the Bika LIMS User Manual. [Sample Point Locations](https://www.bikalims.org/new-manual/samples-and-sampling/sample-point-locations)

### Installation

#### Using Buildout (Classic Plone/Senaite)

Install senaite.samplepointlocations by adding it to your buildout::

    [buildout]

    ...

    eggs =
        senaite.samplepointlocations

and then running ``bin/buildout``

#### Docker (Recommended for Ingwe Bika LIMS 4)

Add senaite.samplepointlocations to your custom add-ons list in the Docker-based Ingwe Bika distribution.

### License
This project is licensed under the GNU General Public License v2.0 (GPL-2.0).

### Support & Professional Services
[Bika Lab Systems](www.bikalabs.com) offers professional implementation, training, custom development, and support for senaite.samplepointlocations.

Website: [https://www.bikalims.org](https://www.bikalims.org)
Email: info@bikalims.org (or contact Lemoene directly)

Made with ❤️ in Cape Town, South Africa
