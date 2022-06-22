# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from senaite.locations.testing import \
    SENAITE_LOCATIONS_INTEGRATION_TESTING  # noqa: E501

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that senaite.locations is properly installed."""

    layer = SENAITE_LOCATIONS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if senaite.locations is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'senaite.locations'))

    def test_browserlayer(self):
        """Test that ISenaiteLocationsLayer is registered."""
        from senaite.locations.interfaces import (
            ISenaiteLocationsLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ISenaiteLocationsLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = SENAITE_LOCATIONS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['senaite.locations'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if senaite.locations is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'senaite.locations'))

    def test_browserlayer_removed(self):
        """Test that ISenaiteLocationsLayer is removed."""
        from senaite.locations.interfaces import \
            ISenaiteLocationsLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            ISenaiteLocationsLayer,
            utils.registered_layers())
