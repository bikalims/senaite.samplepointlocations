# -*- coding: utf-8 -*-
from senaite.locations.content.location import ILocation  # NOQA E501
from senaite.locations.testing import SENAITE_LOCATIONS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class LocationIntegrationTest(unittest.TestCase):

    layer = SENAITE_LOCATIONS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'Client',
            self.portal,
            'parent_container',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_location_schema(self):
        fti = queryUtility(IDexterityFTI, name='Location')
        schema = fti.lookupSchema()
        self.assertEqual(ILocation, schema)

    def test_ct_location_fti(self):
        fti = queryUtility(IDexterityFTI, name='Location')
        self.assertTrue(fti)

    def test_ct_location_factory(self):
        fti = queryUtility(IDexterityFTI, name='Location')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ILocation.providedBy(obj),
            u'ILocation not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_location_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Location',
            id='location',
        )

        self.assertTrue(
            ILocation.providedBy(obj),
            u'ILocation not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('location', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('location', parent.objectIds())

    def test_ct_location_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Location')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_location_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Location')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'location_id',
            title='Location container',
        )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
