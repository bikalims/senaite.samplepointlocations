.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

.. image:: https://travis-ci.org/collective/senaite.samplepointlocations.svg?branch=master
    :target: https://travis-ci.org/collective/senaite.samplepointlocations

.. image:: https://coveralls.io/repos/github/collective/senaite.samplepointlocations/badge.svg?branch=master
    :target: https://coveralls.io/github/collective/senaite.samplepointlocations?branch=master
    :alt: Coveralls

.. image:: https://img.shields.io/pypi/v/senaite.samplepointlocations.svg
    :target: https://pypi.python.org/pypi/senaite.samplepointlocations/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/senaite.samplepointlocations.svg
    :target: https://pypi.python.org/pypi/senaite.samplepointlocations
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/senaite.samplepointlocations.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/senaite.samplepointlocations.svg
    :target: https://pypi.python.org/pypi/senaite.samplepointlocations/
    :alt: License


=================
senaite.samplepointlocations
=================


Features
--------

In some use cases it makes sense to group a number of Sample Points together on their Location, e.g. a number of water Sample Points per village or building complex or lubrication points on a big piece of machinery

Install the Bika add-on senaite.samplepointlocations for this two tier Sample Point addressing to be available

Sample Point Locations* then replaces Sample Points in the UI, and Sample Points are configured 'inside' Locations

Since the Location term is already used for Sample Storage Locations and for Instruments too, the locations here are called Sample Point Locations

Documentation
-------------

Full documentation for end users can be found in the Bika LIMS User Manual at https://www.bikalims.org/manual/setup-and-configuration/4-5-1-sample-point-locations

Examples
--------

Also see the news item, Sample Point Location Feature sponsored by HydroChem Australia, https://www.bikalims.org/news/2-tier-sample-points-sponsored

Installation
------------

Install senaite.samplepointlocations by adding it to your buildout::

    [buildout]

    ...

    eggs =
        senaite.samplepointlocations


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://bika.atlassian.net/jira/software/c/projects/LIMS/boards/2/backlog?selectedIssue=LIMS-21&epics=visible&issueLimit=100
- Source Code: https://github.com/bikalims/senaite.samplepointlocations
- Documentation: https://www.bikalims.org/manual/setup-and-configuration/4-5-1-sample-point-locations


Support
-------

If you are having issues, please let us know at info@bikalabs.com
We have a mailing list located at https://users.bikalims.org
Please request access to the much more active Bika Slack group


License
-------

The project is licensed by the Bika Open Source LIMS Collective, https://www.bikalims.org, under the GPLv2. 
