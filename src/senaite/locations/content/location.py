# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.supermodel import model
from senaite.core.catalog import SETUP_CATALOG
from senaite.locations import _
from zope import schema
from zope.interface import implementer


class ILocation(model.Schema):
    """Marker interface and Dexterity Python Schema for Location"""

    address = schema.TextLine(title=_(u"Address"), required=False)


@implementer(ILocation)
class Location(Container):
    """Content-type class for ILocation"""

    _catalogs = [SETUP_CATALOG]
