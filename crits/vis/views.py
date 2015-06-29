import json
import urllib

from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from crits.core.user_tools import user_can_view_data, user_is_admin
from crits.vis.handlers import generate_vis_graph

@user_passes_test(user_can_view_data)
def vis_graph(request, object_id):
    """
    Generate the a test vis.js display page.

    :param request: Django request.
    :type request: :class:`django.http.HttpRequest`
    :param option: Action to take.
    :type option: str of either 'jtlist', 'jtdelete', 'csv', or 'inline'.
    :returns: :class:`django.http.HttpResponse`
    """

    return generate_vis_graph(request, object_id)
