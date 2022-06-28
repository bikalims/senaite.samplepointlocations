from senaite.locations import check_installed


@check_installed(None)
def getLocation(self):  # noqa camelcase
    """Returns the AR's location"""
    return self.getField("Location").get(self)
