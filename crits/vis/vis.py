import json

class Vis(object):

    """
    Vis class.
    """
    def __init__(self, mydata):
        self.data = mydata

    def _has_method(self, method):
        """
        Convenience method for determining if a method exists for this class.

        :param method: The method to check for.
        :type method: str
        :returns: True, False
        """

        if hasattr(self, method) and callable(getattr(self, method)):
            return True
        else:
            return False

    def to_json(self, exclude=None):
        """
        Convert to JSON.

        :param exclude: list of fields to exclude.
        :type exclude: list
        :returns: json
        """

        return json.dumps(self.data)

