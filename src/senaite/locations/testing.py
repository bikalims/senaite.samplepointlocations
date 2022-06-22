# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import senaite.locations


class SenaiteLocationsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=senaite.locations)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'senaite.locations:default')


SENAITE_LOCATIONS_FIXTURE = SenaiteLocationsLayer()


SENAITE_LOCATIONS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(SENAITE_LOCATIONS_FIXTURE,),
    name='SenaiteLocationsLayer:IntegrationTesting',
)


SENAITE_LOCATIONS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SENAITE_LOCATIONS_FIXTURE,),
    name='SenaiteLocationsLayer:FunctionalTesting',
)


SENAITE_LOCATIONS_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        SENAITE_LOCATIONS_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='SenaiteLocationsLayer:AcceptanceTesting',
)
