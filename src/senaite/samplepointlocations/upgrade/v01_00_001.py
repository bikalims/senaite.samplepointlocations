# -*- coding: utf-8 -*-

from senaite.crms import PRODUCT_NAME
from senaite.crms import PROFILE_ID
from senaite.crms import logger

from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils

version = "1.0.1"


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(PRODUCT_NAME)

    if ut.isOlderVersion(PRODUCT_NAME, version):
        logger.info(
            "Skipping upgrade of {0}: {1} > {2}".format(PRODUCT_NAME, ver_from, version)
        )
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(PRODUCT_NAME, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------

    setup.runImportStepFromProfile(PROFILE_ID, "plone.app.registry")

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def add_location_to_client(portal):
    pt = api.get_tool("portal_types", context=portal)
    fti = pt.get("Client")
    actions = fti.listActions()
    for action in actions:
        if action.id == "samplepointlocations":
            action.title = "Sample Point Locations"
            logger.info("Changed action title to Sample Point Location")
