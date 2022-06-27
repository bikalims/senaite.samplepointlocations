# -*- coding: utf-8 -*-
"""Init and utils."""
from AccessControl.Permission import addPermission
from AccessControl.SecurityInfo import ModuleSecurityInfo
import logging
from senaite.api import get_request
from senaite.locations.interfaces import ISenaiteLocationsLayer
from senaite.locations import permissions
from zope.i18nmessageid import MessageFactory

security = ModuleSecurityInfo("senaite.patient")

PRODUCT_NAME = "senaite.locations"
PROFILE_ID = "profile-{}:default".format(PRODUCT_NAME)
DEFAULT_ROLES = ("Manager",)
DEFAULT_TYPES = ("Location",)

logger = logging.getLogger(PRODUCT_NAME)

_ = MessageFactory(PRODUCT_NAME)


def is_installed():
    """Returns whether the product is installed or not"""
    request = get_request()
    return ISenaiteLocationsLayer.providedBy(request)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    logger.info("*** Initializing SENAITE LOCATION addon package ***")
    from senaite.locations.content.location import Location  # noqa

    # Set add permissions
    for typename in DEFAULT_TYPES:
        permid = "Add" + typename
        permname = getattr(permissions, permid)
        security.declarePublic(permid)
        addPermission(permname, default_roles=DEFAULT_ROLES)
