# -*- coding: utf-8 -*-

from senaite.core.upgrade import upgradestep
from senaite.samplepointlocations import PRODUCT_NAME
from senaite.samplepointlocations import logger
from senaite.samplepointlocations.permissions import setup_default_permissions

version = "1.0.2"


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup_default_permissions(portal)
    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True
