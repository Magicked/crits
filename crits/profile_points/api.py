import datetime

from django.core.urlresolvers import reverse
from tastypie import authorization
from tastypie.authentication import MultiAuthentication

from crits.profile_points.profile_point import ProfilePoint
from crits.profile_points.handlers import handle_profile_point_ind
from crits.profile_points.handlers import activity_add
from crits.core.api import CRITsApiKeyAuthentication
from crits.core.api import CRITsSessionAuthentication
from crits.core.api import CRITsSerializer, CRITsAPIResource


class ProfilePointResource(CRITsAPIResource):
    """
    Class to handle everything related to the Backdoor API.

    Currently supports GET and POST.
    """

    class Meta:
        object_class = ProfilePoint
        allowed_methods = ('get', 'post', 'patch')
        resource_name = "profile_points"
        authentication = MultiAuthentication(CRITsApiKeyAuthentication(),
                                             CRITsSessionAuthentication())
        authorization = authorization.Authorization()
        serializer = CRITsSerializer()

    def get_object_list(self, request):
        """
        Use the CRITsAPIResource to get our objects but provide the class to
        get the objects from.

        :param request: The incoming request.
        :type request: :class:`django.http.HttpRequest`
        :returns: Resulting objects in the specified format (JSON by default).

        """

        return super(ProfilePointResource, self).get_object_list(request,
                                                                 ProfilePoint)

    def obj_create(self, bundle, **kwargs):
        """
        Handles creating Profile Points through the API.

        :param bundle: Bundle containing the information to create the Profile
                      Point.
        :type bundle: Tastypie Bundle object.
        :returns: HttpResponse object.
        """

        user = bundle.request.user.username
        value = bundle.data.get('value', None)
        status = bundle.data.get('status', None)
        source = bundle.data.get('source', None)
        reference = bundle.data.get('reference', None)
        method = bundle.data.get('method', None)
        campaign = bundle.data.get('campaign', None)
        cc = bundle.data.get('campaign_confidence', None)
        bucket_list = bundle.data.get('bucket_list', None)
        ticket = bundle.data.get('ticket', None)

        result = handle_profile_point_ind(value,
                                          source,
                                          user,
                                          status=status,
                                          method=method,
                                          reference=reference,
                                          campaign=campaign,
                                          campaign_confidence=cc,
                                          bucket_list=bucket_list,
                                          ticket=ticket)

        content = {'return_code': 0,
                   'type': 'ProfilePoint'}
        if result.get('message'):
            content['message'] = result.get('message')
        if result.get('objectid'):
            url = reverse('api_dispatch_detail',
                          kwargs={'resource_name': 'profile_points',
                                  'api_name': 'v1',
                                  'pk': result.get('objectid')})
            content['id'] = result.get('objectid')
            content['url'] = url
        if not result['success']:
            content['return_code'] = 1
        self.crits_response(content)


class ProfilePointActivityResource(CRITsAPIResource):
    """
    Class to handle Profile Point Activity.

    Currently supports POST.
    """

    class Meta:
        object_class = ProfilePoint
        allowed_methods = ('post',)
        resource_name = "profile_point_activity"
        authentication = MultiAuthentication(CRITsApiKeyAuthentication(),
                                             CRITsSessionAuthentication())
        authorization = authorization.Authorization()
        serializer = CRITsSerializer()

    def get_object_list(self, request):
        """
        Use the CRITsAPIResource to get our objects but provide the class to
        get the objects from.

        :param request: The incoming request.
        :type request: :class:`django.http.HttpRequest`
        :returns: Resulting objects in the specified format (JSON by default).
        """

        return super(ProfilePointActivityResource, self).get_object_list(
                                                          request,
                                                          ProfilePoint)

    def obj_create(self, bundle, **kwargs):
        """
        Handles adding ProfilePoint Activity through the API.

        :param bundle: Bundle containing the information to add the Activity.
        :type bundle: Tastypie Bundle object.
        :returns: HttpResponse.
        """

        analyst = bundle.request.user.username
        object_id = bundle.data.get('object_id', None)
        start_date = bundle.data.get('start_date', None)
        end_date = bundle.data.get('end_date', None)
        description = bundle.data.get('description', None)

        content = {'return_code': 1,
                   'type': 'ProfilePoint'}

        if not object_id or not description:
            content['message'] = 'Must provide object_id and description.'
            self.crits_response(content)

        activity = {'analyst': analyst,
                    'start_date': start_date,
                    'end_date': end_date,
                    'description': description,
                    'date': datetime.datetime.now()}
        result = activity_add(object_id, activity)
        if not result['success']:
            content['message'] = result['message']
            self.crits_response(content)

        if result.get('message'):
            content['message'] = result.get('message')
        if result.get('id'):
            url = reverse('api_dispatch_detail',
                          kwargs={'resource_name': 'indicators',
                                  'api_name': 'v1',
                                  'pk': result.get('id')})
            content['id'] = result.get('id')
            content['url'] = url
        if result['success']:
            content['return_code'] = 0
        self.crits_response(content)
