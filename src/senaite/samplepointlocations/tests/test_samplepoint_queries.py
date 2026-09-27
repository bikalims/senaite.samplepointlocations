import os
import unittest
from xml.etree import ElementTree

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex
from plone.dexterity.content import Container
from senaite.samplepointlocations.monkeys import analysisrequest as add


CLIENT = "a" * 32
LOCATION = "b" * 32
SAMPLE_TYPE = "c" * 32
OTHER = "d" * 32


class AddView(object):
    get_client_queries = add.get_client_queries
    get_sampletype_queries = add.get_sampletype_queries
    get_samplepointlocation_queries = add.get_samplepointlocation_queries

    def get_client(self):
        return CLIENT


class Point(object):
    def __init__(self, location, sample_type):
        self.getSamplePointLocationUID = location
        self.sampletype_uid = [sample_type]
        self.getClientUID = CLIENT


class SamplePointQueriesTest(unittest.TestCase):
    def setUp(self):
        self.view = AddView()
        self.record = {"Client": CLIENT, "SampleType": SAMPLE_TYPE,
                       "SamplePointLocation": LOCATION}
        self.catalog = ZCatalog("points")
        for name, factory in [("getSamplePointLocationUID", FieldIndex),
                              ("sampletype_uid", KeywordIndex),
                              ("getClientUID", FieldIndex)]:
            self.catalog._catalog.addIndex(name, factory(name))
        self.catalog.catalog_object(Point(LOCATION, OTHER), "point")
        self.catalog.catalog_object(Point(OTHER, SAMPLE_TYPE), "elsewhere")

    def matches(self, query):
        return sorted(brain.getPath() for brain in self.catalog(query))

    def test_location_keeps_point_with_different_sample_type(self):
        queries = self.view.get_sampletype_queries(SAMPLE_TYPE, self.record)
        self.assertEqual(self.matches(queries["SamplePoint"]), ["point"])
        self.assertEqual(queries["Profiles"]["sampletype_uid"],
                         [SAMPLE_TYPE, ""])
        self.assertEqual(queries["Specification"]["sampletype_uid"], SAMPLE_TYPE)

    def test_all_metadata_sources_allow_same_points(self):
        sources = [self.view.get_client_queries(CLIENT, self.record),
                   self.view.get_sampletype_queries(SAMPLE_TYPE, self.record),
                   self.view.get_samplepointlocation_queries(LOCATION, self.record)]
        for queries in sources:
            self.assertEqual(self.matches(queries["SamplePoint"]), ["point"])
            self.assertEqual(queries["SamplePoint"], sources[0]["SamplePoint"])

    def test_clearing_location_restores_type_filter(self):
        self.record["SamplePointLocation"] = ""
        queries = self.view.get_sampletype_queries(SAMPLE_TYPE, self.record)
        self.assertEqual(self.matches(queries["SamplePoint"]), ["elsewhere"])

    def test_location_filters_without_sample_type(self):
        del self.record["SampleType"]
        queries = self.view.get_client_queries(CLIENT, self.record)
        self.assertEqual(self.matches(queries["SamplePoint"]), ["point"])

    def test_missing_record_uses_core_type_filter(self):
        queries = self.view.get_sampletype_queries(SAMPLE_TYPE)
        self.assertEqual(self.matches(queries["SamplePoint"]), ["elsewhere"])

    def test_changing_location_replaces_previous_location(self):
        queries = self.view.get_samplepointlocation_queries(OTHER, self.record)
        self.assertEqual(self.matches(queries["SamplePoint"]), ["elsewhere"])

    def test_client_scope_is_preserved(self):
        self.record["Client"] = OTHER
        queries = self.view.get_sampletype_queries(SAMPLE_TYPE, self.record)
        self.assertEqual(self.matches(queries["SamplePoint"]), [])

    def test_location_query_registered_on_add_view(self):
        path = os.path.join(os.path.dirname(add.__file__), "configure.zcml")
        patches = ElementTree.parse(path).getroot()
        patch = [node for node in patches
                 if node.get("original") == "get_samplepointlocation_queries"][0]
        self.assertEqual(patch.get("class"),
                         "bika.lims.browser.analysisrequest.add2.ajaxAnalysisRequestAddView")


class SamplePointMetadataTest(unittest.TestCase):
    def setUp(self):
        self.location = Container("location")
        self.location.portal_type = "SamplePointLocation"
        self.location.title = u"Location"
        self.location.UID = lambda: LOCATION
        self.sample_type = Container("type")
        self.sample_type.title = u"Other type"
        self.sample_type.UID = lambda: OTHER
        self.point = Container("point").__of__(self.location)
        self.point.sample_point_location = [LOCATION]
        self.point.getSampleTypes = lambda: [self.sample_type]
        self.original_lookup = add.api.get_object_by_uid
        objects = {LOCATION: self.location, OTHER: self.sample_type}
        add.api.get_object_by_uid = objects.get
        self.info = {"field_values": {}, "filter_queries": {}}

    def tearDown(self):
        add.api.get_object_by_uid = self.original_lookup

    def test_point_preserves_selected_type_and_location(self):
        info = add.get_samplepoint_info(self.point, self.info, CLIENT,
                                       {"SampleType": SAMPLE_TYPE,
                                        "SamplePointLocation": LOCATION})
        self.assertNotIn("SampleType", info["filter_queries"])
        self.assertTrue(info["field_values"]["SampleType"]["if_empty"])
        self.assertTrue(info["field_values"]["SamplePointLocation"]["if_empty"])

    def test_reference_location_is_used_instead_of_parent(self):
        client = Container("client")
        client.portal_type = "Client"
        self.point = self.point.aq_base.__of__(client)
        info = add.get_samplepoint_info(self.point, self.info, CLIENT)
        self.assertEqual(info["field_values"]["SamplePointLocation"]["uid"], LOCATION)
        self.assertNotIn("SampleType", info["filter_queries"])

    def test_unlocated_point_does_not_restrict_type_when_location_selected(self):
        self.point.sample_point_location = []
        self.location.portal_type = "Client"
        info = add.get_samplepoint_info(self.point, self.info, CLIENT,
                                       {"SamplePointLocation": LOCATION})
        self.assertNotIn("SampleType", info["filter_queries"])
        self.assertNotIn("SamplePointLocation", info["field_values"])

    def test_unlocated_point_retains_original_type_filter(self):
        self.point.sample_point_location = []
        self.location.portal_type = "Client"
        info = add.get_samplepoint_info(self.point, self.info, CLIENT)
        self.assertEqual(info["filter_queries"]["SampleType"], {"UID": [OTHER]})
        self.assertNotIn("SamplePointLocation", info["field_values"])


if __name__ == "__main__":
    unittest.main()
