from collections import OrderedDict
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter
from senaite.api import get_object
from senaite.samplepointlocations import _
from senaite.samplepointlocations import is_installed
from zope.component import adapts
from zope.interface import implements


class SamplesListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return
        new_columns = OrderedDict(
            (
                (
                    "location",
                    dict(title=_("Sample Point Location"), sortable=False, toggle=True),
                ),
            )
        )
        self.listing.columns.update(new_columns)

        # Apply the columns to all review_states
        keys = self.listing.columns.keys()
        map(lambda rv: rv.update({"columns": keys}), self.listing.review_states)

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item
        obj = get_object(obj)
        field = obj.Schema().getField("SamplePointLocation")
        if field:
            loc = field.get(obj)
            item["location"] = loc.title if loc else ""
        else:
            item["location"] = ""
        return item
