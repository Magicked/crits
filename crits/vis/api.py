from django.core.urlresolvers import reverse
from tastypie import authorization
from tastypie.authentication import MultiAuthentication
from tastypie.exceptions import BadRequest
from tastypie.resources import Resource

from crits.vis.handlers import generate_vis_graph
from crits.core.api import CRITsApiKeyAuthentication, CRITsSessionAuthentication
from crits.core.api import CRITsSerializer, CRITsAPIResource
from crits.vis.vis import Vis

class dict2obj(object):
    """
    Convert dictionary to object
    @source http://stackoverflow.com/a/1305561/383912
    """
    def __init__(self, d):
        self.__dict__['d'] = d

    def __getattr__(self, key):
        value = self.__dict__['d'][key]
        if type(value) == type({}):
            return dict2obj(value)
        return value

class VisResource(Resource):
    """
    Class to handle everything related to the Vis.js API.

    Currently supports GET.
    """

    class Meta:
        allowed_methods = ('get')
        resource_name = "vis"
        authentication = MultiAuthentication(CRITsApiKeyAuthentication(),
                                             CRITsSessionAuthentication())
        authorization = authorization.Authorization()
        serializer = CRITsSerializer()

    def get_object_list(self, request):
        """
        Use the CRITsAPIResource to get our objects but provide the class to get
        the objects from.

        :param request: The incoming request.
        :type request: :class:`django.http.HttpRequest`
        :returns: Resulting objects in the specified format (JSON by default).
        """
        # Chop off trailing slash and split on remaining slashes.
        # If last part of path is not the resource name, assume it is an object ID.
        path = request.path[:-1].split('/')
        obj_id = ''
        if path[-1] != self.Meta.resource_name:
            obj_id = path[-1]

        json_data = generate_vis_graph('nhausrath', obj_id)[1]
        visobj = Vis(json_data)

        return [ visobj ]

    def obj_get_list(self, bundle, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(bundle.request)

    def obj_get(self, bundle, **kwargs):
        # This thing only returns one object
        return self.get_object_list(bundle.request)[0]

    def determine_format(self, request):
        return 'application/json'
