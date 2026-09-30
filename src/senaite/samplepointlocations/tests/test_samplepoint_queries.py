import os
import unittest
from xml.etree import ElementTree

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex
from plone.dexterity.content import Container
from senaite.samplepointlocations.monkeys import analysisrequest as add
from senaite.samplepointlocations.adapters.referencewidget import vocabularies


CLIENT = "a" * 32
LOCATION = "b" * 32
SAMPLE_TYPE = "c" * 32
OTHER = "d" * 32


class AddView(object):
    get_client_queries = add.get_client_queries
    get_sampletype_queries = add.get_sampletype_queries
    get_samplepointlocation_queries = add.get_samplepointlocation_queries
    get_object_info = add.get_object_info

    def get_base_info(self, obj):
        return {"uid": add.api.get_uid(obj), "field_values": {}}

    def update_object_info(self, info, additional):
        for key in ("field_values", "filter_queries"):
            info.setdefault(key, {}).update(additional.get(key, {}))

    def get_client(self):
        return CLIENT


class Point(object):
    def __init__(self, location, sample_type):
        self.getSamplePointLocationUID = location
        self.sampletype_uid = [sample_type]
        self.getClientUID = CLIENT
        self.UID = location


class SamplePointQueriesTest(unittest.TestCase):
    def setUp(self):
        self.view = AddView()
        self.record = {"Client": CLIENT, "SampleType": SAMPLE_TYPE,
                       "SamplePointLocation": LOCATION}
        self.catalog = ZCatalog("points")
        for name, factory in [("UID", FieldIndex),
                              ("getSamplePointLocationUID", FieldIndex),
                              ("sampletype_uid", KeywordIndex),
                              ("getClientUID", FieldIndex)]:
            self.catalog._catalog.addIndex(name, factory(name))
        self.catalog.catalog_object(Point(LOCATION, OTHER), "point")
        self.catalog.catalog_object(Point(OTHER, SAMPLE_TYPE), "elsewhere")

    def matches(self, query):
        return sorted(brain.getPath() for brain in self.catalog(query))

    def test_location_keeps_point_with_different_sample_type(self):
        queries = self.view.get_sampletype_queries(SAMPLE_TYPE, self.record)
        self.assertNotIn("SamplePoint", queries)
        self.assertEqual(self.matches(add.get_samplepoint_query(self.view, self.record)), ["point"])
        self.assertEqual(queries["Profiles"]["sampletype_uid"],
                         [SAMPLE_TYPE, ""])
        self.assertEqual(queries["Specification"]["sampletype_uid"], SAMPLE_TYPE)

    def test_all_metadata_sources_allow_same_points(self):
        sources = [self.view.get_client_queries(CLIENT, self.record),
                   self.view.get_samplepointlocation_queries(LOCATION, self.record)]
        for queries in sources:
            self.assertEqual(self.matches(queries["SamplePoint"]), ["point"])
            self.assertEqual(queries["SamplePoint"], sources[0]["SamplePoint"])

    def test_empty_column_cannot_overwrite_selected_column_location(self):
        cached = {"uid": CLIENT, "field_values": {}, "filter_queries": {}}
        self.view.get_base_info = lambda obj: cached
        selected = self.view.get_object_info(CLIENT, "Client", self.record)
        empty = self.view.get_object_info(CLIENT, "Client", {"Client": CLIENT})
        self.assertEqual(selected["filter_queries"]["SamplePoint"],
                         {"getSamplePointLocationUID": LOCATION,
                          "getClientUID": [CLIENT, ""]})
        self.assertEqual(empty["filter_queries"]["SamplePoint"]["UID"], "")
        self.assertEqual(cached["filter_queries"], {})

    def test_cached_field_values_are_not_shared_between_columns(self):
        cached = {"uid": CLIENT, "field_values": {"Nested": {"value": []}},
                  "filter_queries": {}}
        self.view.get_base_info = lambda obj: cached
        first = self.view.get_object_info(CLIENT, "Client", self.record)
        first["field_values"]["Nested"]["value"].append("first column")
        second = self.view.get_object_info(CLIENT, "Client", self.record)
        self.assertEqual(second["field_values"]["Nested"]["value"], [])

    def test_clearing_location_empties_points(self):
        self.record["SamplePointLocation"] = ""
        query = add.get_samplepoint_query(self.view, self.record)
        self.assertEqual(self.matches(query), [])

    def test_location_filters_without_sample_type(self):
        del self.record["SampleType"]
        queries = self.view.get_client_queries(CLIENT, self.record)
        self.assertEqual(self.matches(queries["SamplePoint"]), ["point"])

    def test_missing_record_does_not_filter_points_by_type(self):
        queries = self.view.get_sampletype_queries(SAMPLE_TYPE)
        self.assertNotIn("SamplePoint", queries)

    def test_changing_location_replaces_previous_location(self):
        queries = self.view.get_samplepointlocation_queries(OTHER, self.record)
        self.assertEqual(self.matches(queries["SamplePoint"]), ["elsewhere"])

    def test_client_scope_is_preserved(self):
        self.record["Client"] = OTHER
        query = add.get_samplepoint_query(self.view, self.record)
        self.assertEqual(self.matches(query), [])

    def test_locations_follow_context_client(self):
        query = add.get_cascade_queries(self.view, {})["SamplePointLocation"]
        self.assertEqual(query, {"getClientUID": [CLIENT, ""]})

    def test_locations_follow_selected_client(self):
        query = add.get_cascade_queries(self.view, {"Client": OTHER})["SamplePointLocation"]
        self.assertEqual(query, {"getClientUID": [OTHER, ""]})

    def test_types_wait_for_point(self):
        query = add.get_cascade_queries(self.view, self.record)["SampleType"]
        self.assertEqual(query, {"UID": ""})

    def test_unassigned_points_are_excluded(self):
        self.catalog.catalog_object(Point("", SAMPLE_TYPE), "unassigned")
        query = add.get_samplepoint_query(self.view, self.record)
        self.assertEqual(self.matches(query), ["point"])

    def test_global_points_in_selected_location_remain_available(self):
        global_point = Point(LOCATION, SAMPLE_TYPE)
        global_point.getClientUID = ""
        self.catalog.catalog_object(global_point, "global")
        other_location = Point(OTHER, SAMPLE_TYPE)
        other_location.getClientUID = ""
        self.catalog.catalog_object(other_location, "global-elsewhere")
        query = add.get_samplepoint_query(self.view, self.record)
        self.assertEqual(self.matches(query), ["global", "point"])

    def test_location_filter_keeps_globals_but_excludes_other_clients(self):
        global_location = Point(LOCATION, SAMPLE_TYPE)
        global_location.getClientUID = ""
        self.catalog.catalog_object(global_location, "global")
        foreign_location = Point(OTHER, SAMPLE_TYPE)
        foreign_location.getClientUID = OTHER
        self.catalog.catalog_object(foreign_location, "foreign")
        query = add.get_cascade_queries(self.view, self.record)["SamplePointLocation"]
        self.assertEqual(self.matches(query), ["elsewhere", "global", "point"])

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

    def test_point_filters_type_without_changing_location(self):
        info = add.get_samplepoint_info(self.point, self.info, CLIENT,
                                       {"SampleType": SAMPLE_TYPE,
                                        "SamplePointLocation": LOCATION})
        self.assertEqual(info["filter_queries"]["SampleType"], {"UID": [OTHER]})
        self.assertEqual(info["field_values"]["SampleType"]["uid"], OTHER)
        self.assertNotIn("SamplePointLocation", info["field_values"])

    def test_reference_location_is_used_instead_of_parent(self):
        client = Container("client")
        client.portal_type = "Client"
        self.point = self.point.aq_base.__of__(client)
        info = add.get_samplepoint_info(self.point, self.info, CLIENT)
        self.assertNotIn("SamplePointLocation", info["field_values"])
        self.assertEqual(info["filter_queries"]["SampleType"], {"UID": [OTHER]})

    def test_point_restricts_type_when_location_selected(self):
        self.point.sample_point_location = []
        self.location.portal_type = "Client"
        info = add.get_samplepoint_info(self.point, self.info, CLIENT,
                                       {"SamplePointLocation": LOCATION})
        self.assertEqual(info["filter_queries"]["SampleType"], {"UID": [OTHER]})
        self.assertNotIn("SamplePointLocation", info["field_values"])

    def test_unlocated_point_retains_original_type_filter(self):
        self.point.sample_point_location = []
        self.location.portal_type = "Client"
        info = add.get_samplepoint_info(self.point, self.info, CLIENT)
        self.assertEqual(info["filter_queries"]["SampleType"], {"UID": [OTHER]})
        self.assertNotIn("SamplePointLocation", info["field_values"])

    def test_cascade_type_query_uses_selected_point(self):
        add.api.get_object_by_uid = lambda uid: self.point
        query = add.get_cascade_queries(AddView(), {"SamplePoint": LOCATION})
        self.assertEqual(query["SampleType"], {"UID": [OTHER]})

    def test_point_without_assigned_types_allows_any_type(self):
        self.point.getSampleTypes = lambda: []
        add.api.get_object_by_uid = lambda uid: self.point
        query = add.get_cascade_queries(AddView(), {"SamplePoint": LOCATION})
        self.assertEqual(query["SampleType"], {})

    def test_type_metadata_does_not_revalidate_point_or_type(self):
        # The form record can still contain the previous point during a change.
        info = AddView().get_object_info(self.sample_type, "SampleType",
                                        {"SamplePoint": ""})
        self.assertNotIn("SamplePoint", info["filter_queries"])
        self.assertNotIn("SampleType", info["filter_queries"])
        self.assertNotIn("SamplePointLocation", info["filter_queries"])

    def test_point_metadata_only_filters_types_with_stale_record(self):
        self.point.UID = lambda: LOCATION
        info = AddView().get_object_info(self.point, "SamplePoint",
                                        {"SamplePointLocation": "",
                                         "SamplePoint": ""})
        self.assertEqual(info["filter_queries"], {"SampleType": {"UID": [OTHER]}})

    def test_unrestricted_point_resets_previous_type_query(self):
        self.point.getSampleTypes = lambda: []
        info = add.get_samplepoint_info(self.point, self.info, CLIENT)
        self.assertEqual(info["filter_queries"], {"SampleType": {}})


class Vocabulary(vocabularies.ClientAwareReferenceWidgetVocabulary):
    @property
    def query(self):
        return dict(self.request)


class DropdownCascadeTest(unittest.TestCase):
    def setUp(self):
        self.client = Container("client")
        self.client.UID = lambda: CLIENT
        original = vocabularies.get_client
        vocabularies.get_client = lambda context: self.client
        self.addCleanup(setattr, vocabularies, "get_client", original)

    def test_initial_locations_use_client_context(self):
        query = Vocabulary(None, {"portal_type": "SamplePointLocation"}).get_raw_query()
        self.assertEqual(query["getClientUID"], [CLIENT, ""])

    def test_selected_client_overrides_context(self):
        query = Vocabulary(None, {"portal_type": "SamplePointLocation",
                                  "getClientUID": OTHER}).get_raw_query()
        self.assertEqual(query["getClientUID"], OTHER)

    def test_unsaved_location_overrides_context_location(self):
        location = Container("old-location")
        location.UID = lambda: OTHER
        self.client.getSamplePointLocation = lambda: location
        query = Vocabulary(self.client, {"portal_type": "SamplePoint",
                                         "field_name": "SamplePoint-0",
                                         "getSamplePointLocationUID": LOCATION,
                                         "sampletype_uid": SAMPLE_TYPE}).get_raw_query()
        self.assertEqual(query["getSamplePointLocationUID"], LOCATION)
        self.assertNotIn("sampletype_uid", query)

    def test_no_location_means_no_points(self):
        query = Vocabulary(None, {"portal_type": "SamplePoint",
                                  "field_name": "SamplePoint-0"}).get_raw_query()
        self.assertEqual(query["UID"], "")

    def test_selected_reference_labels_can_still_be_resolved(self):
        query = Vocabulary(None, {"portal_type": "SamplePoint", "UID": OTHER}).get_raw_query()
        self.assertEqual(query["UID"], OTHER)

    def test_no_client_means_no_locations(self):
        vocabularies.get_client = lambda context: None
        query = Vocabulary(None, {"portal_type": "SamplePointLocation",
                                  "field_name": "SamplePointLocation-0"}).get_raw_query()
        self.assertEqual(query["UID"], "")

    def test_other_forms_can_search_points_without_a_location(self):
        query = Vocabulary(None, {"portal_type": "SamplePoint"}).get_raw_query()
        self.assertNotIn("UID", query)


if __name__ == "__main__":
    unittest.main()
