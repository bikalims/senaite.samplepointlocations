from bika.lims.utils import get_client
import json
from Products.Archetypes.Registry import registerWidget
from senaite import api
from senaite.core.browser.widgets import ReferenceWidget
import six


class ClientAwareReferenceWidget(ReferenceWidget):
    _properties = ReferenceWidget._properties.copy()

    def get_base_query(self, context, fieldName):
        base_query = self.base_query
        if callable(base_query):
            try:
                base_query = base_query(context, self, fieldName)
            except TypeError:
                base_query = base_query()
        if base_query and isinstance(base_query, six.string_types):
            base_query = json.loads(base_query)

        # portal_type: use field allowed types
        field = context.Schema().getField(fieldName)
        allowed_types = getattr(field, "allowed_types", [])
        allowed_types_method = getattr(field, "allowed_types_method", None)
        if allowed_types_method:
            meth = getattr(context, allowed_types_method)
            allowed_types = meth(field)
        # If field has no allowed_types defined, use widget"s portal_type prop
        base_query["portal_type"] = (
            allowed_types if allowed_types else self.portal_types
        )
        client = get_client(context)
        client_uid = client and api.get_uid(client) or None

        if client_uid:
            # Apply the search criteria for this client
            # Contact is the only object bound to a Client that is stored
            # in portal_catalog. And in this catalog, getClientUID does not
            # exist, rather getParentUID
            if "Contact" in allowed_types:
                base_query["getParentUID"] = [client_uid]
            else:
                base_query["getClientUID"] = [client_uid, ""]
        return base_query


registerWidget(ClientAwareReferenceWidget, title="Client aware Reference Widget")
