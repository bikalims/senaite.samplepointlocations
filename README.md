## senaite.samplepointlocations

### Features

In some use cases it makes sense to group a number of Sample Points together on their Location, e.g. a number of water Sample Points per village or building complex or lubrication points on a big piece of machinery

Install the Bika add-on senaite.samplepointlocations for this two tier Sample Point addressing to be available

Sample Point Locations* then replaces Sample Points in the UI, and Sample Points are configured 'inside' Locations

Since the Location term is already used for Sample Storage Locations and for Instruments too, the locations here are called Sample Point Locations

### Documentation

Full documentation for end users can be found in the Bika LIMS User Manual. [Sample Point Locations](https://www.bikalims.org/new-manual/samples-and-sampling/sample-point-locations)

### Installation

Install senaite.samplepointlocations by adding it to your buildout::

    [buildout]

    ...

    eggs =
        senaite.samplepointlocations


and then running ``bin/buildout``


License
-------

The project is licensed by the [Bika Open Source LIMS Collective](https://www.bikalims.org), under the GPLv2. 
