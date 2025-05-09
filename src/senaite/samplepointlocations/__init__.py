# -*- coding: utf-8 -*-
"""Init and utils."""
from AccessControl.Permission import addPermission
from AccessControl.SecurityInfo import ModuleSecurityInfo
import logging
from bika.lims.api import get_request
from senaite.samplepointlocations.interfaces import ISenaiteSamplePointLocationsLayer
from senaite.samplepointlocations import permissions
from zope.i18nmessageid import MessageFactory

security = ModuleSecurityInfo("senaite.patient")

PRODUCT_NAME = "senaite.samplepointlocations"
PROFILE_ID = "profile-{}:default".format(PRODUCT_NAME)
DEFAULT_ROLES = ("Manager",)
DEFAULT_TYPES = ("SamplePointLocation",)

logger = logging.getLogger(PRODUCT_NAME)

_ = MessageFactory(PRODUCT_NAME)


def is_installed():
    """Returns whether the product is installed or not"""
    request = get_request()
    return ISenaiteSamplePointLocationsLayer.providedBy(request)


def check_installed(default_return):
    """Decorator to prevent the function to be called if product not installed
    :param default_return: value to return if not installed
    """

    def is_installed_decorator(func):
        def wrapper(*args, **kwargs):
            if not is_installed():
                return default_return
            if "field" in kwargs:
                return default_return
            return func(*args, **kwargs)

        return wrapper

    return is_installed_decorator


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    logger.info("*** Initializing SENAITE SAMPLEPOINTLOCATION addon package ***")
    from senaite.samplepointlocations.content.samplepointlocation import SamplePointLocation  # fmt: skip

    # Set add permissions
    for typename in DEFAULT_TYPES:
        permid = "Add" + typename
        permname = getattr(permissions, permid)
        security.declarePublic(permid)
        addPermission(permname, default_roles=DEFAULT_ROLES)
