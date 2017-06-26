import datetime
import json
import urllib

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from crits.core.crits_mongoengine import json_handler
from crits.core.user_tools import user_can_view_data, is_admin
from crits.core import form_consts
from crits.profile_points.forms import UploadProfilePointCSVForm
from crits.profile_points.forms import UploadProfilePointForm, UploadProfilePointTextForm
from crits.profile_points.forms import ProfilePointActivityForm
from crits.profile_points.handlers import (
    profile_point_remove,
    handle_profile_point_csv,
    handle_profile_point_ind,
    activity_add,
    activity_update,
    activity_remove,
    ci_update,
    create_profile_point_and_ip,
    set_profile_point_type,
    modify_threat_types,
    modify_attack_types,
    get_profile_point_details,
    generate_profile_point_jtable,
    generate_profile_point_csv,
    create_profile_point_from_tlo
)


@user_passes_test(user_can_view_data)
def profile_point(request, profile_point_id):
    """
    Generate ProfilePoint Details template.

    :param request: Django request object (Required)
    :type request: :class:`django.http.HttpRequest`
    :param profile_point_id: The ObjectId of the profile_point to get details for.
    :type profile_point_id: str
    :returns: :class:`django.http.HttpResponse`
    """

    analyst = request.user.username
    template = "profile_point_detail.html"
    (new_template, args) = get_profile_point_details(profile_point_id,
                                                     analyst)
    if new_template:
        template = new_template
    return render_to_response(template,
                              args,
                              RequestContext(request))


@user_passes_test(user_can_view_data)
def profile_points_listing(request, option=None):
    """
    Generate ProfilePoint Listing template.

    :param request: Django request object (Required)
    :type request: :class:`django.http.HttpRequest`
    :param option: Whether or not we should generate a CSV
                   (yes if option is "csv")
    :type option: str
    :returns: :class:`django.http.HttpResponse`
    """

    if option == "csv":
        return generate_profile_point_csv(request)
    return generate_profile_point_jtable(request, option)


@user_passes_test(user_can_view_data)
def remove_profile_point(request, _id):
    """
    Remove an ProfilePoint from CRITs.

    :param request: Django request object (Required)
    :type request: :class:`django.http.HttpRequest`
    :param _id: The ObjectId of the profile_point to remove.
    :type _id: str
    :returns: :class:`django.http.HttpResponse`,
              :class:`django.http.HttpResponseRedirect`
    """

    result = profile_point_remove(_id,
                                  '%s' % request.user.username)
    if result['success']:
        return HttpResponseRedirect(reverse('crits.profile_points.views.profile_points_listing'))
    else:
        return render_to_response('error.html',
                                  {'error': result['message']})


@user_passes_test(user_can_view_data)
def profile_point_search(request):
    """
    Search for profile_points.

    :param request: Django request object (Required)
    :type request: :class:`django.http.HttpRequest`
    :returns: :class:`django.http.HttpResponseRedirect`
    """

    query = {}
    query[request.GET.get('search_type', '')] = request.GET.get('q', '').strip()
    return HttpResponseRedirect(reverse('crits.profile_points.views.profile_points_listing')
                                + "?%s" % urllib.urlencode(query))


@user_passes_test(user_can_view_data)
def upload_profile_point(request):
    """
    Upload new profile_points (individual, blob, or CSV file).

    :param request: Django request object (Required)
    :type request: :class:`django.http.HttpRequest`
    :returns: :class:`django.http.HttpResponse`
              :class:`django.http.HttpResponseRedirect`
    """

    if request.method == "POST":
        username = request.user.username
        failed_msg = ''
        result = None

        if request.POST['svalue'] == "Upload CSV":
            form = UploadProfilePointCSVForm(
                username,
                request.POST,
                request.FILES)
            if form.is_valid():
                result = handle_profile_point_csv(request.FILES['filedata'],
                                                  request.POST['source'],
                                                  request.POST['method'],
                                                  request.POST['reference'],
                                                  "file",
                                                  username)
                if result['success']:
                    message = {'message': ('<div>%s <a href="%s">Go to all'
                                           ' profile_points</a></div>' %
                                           (result['message'],
                                            reverse('crits.profile_points.views.profile_points_listing')))}
                else:
                    failed_msg = '<div>%s</div>' % result['message']

        if request.POST['svalue'] == "Upload Text":
            form = UploadProfilePointTextForm(username, request.POST)
            if form.is_valid():
                result = handle_profile_point_csv(request.POST['data'],
                                                  request.POST['source'],
                                                  request.POST['method'],
                                                  request.POST['reference'],
                                                  "ti",
                                                  username)
                if result['success']:
                    message = {'message': ('<div>%s <a href="%s">Go to all'
                                           ' profile_points</a></div>' %
                                           (result['message'],
                                            reverse('crits.profile_points.views.profile_points_listing')))}
                else:
                    failed_msg = '<div>%s</div>' % result['message']

        if request.POST['svalue'] == "Upload ProfilePoint":
            form = UploadProfilePointForm(username,
                                          request.POST)
            if form.is_valid():
                result = handle_profile_point_ind(
                    request.POST['value'],
                    request.POST['source'],
                    username,
                    status=request.POST['status'],
                    method=request.POST['method'],
                    reference=request.POST['reference'],
                    campaign=request.POST['campaign'],
                    campaign_confidence=request.POST['campaign_confidence'],
                    impact=request.POST['impact'],
                    bucket_list=request.POST[form_consts.Common.BUCKET_LIST_VARIABLE_NAME],
                    ticket=request.POST[form_consts.Common.TICKET_VARIABLE_NAME])
                if result['success']:
                    profile_point_link = ((' - <a href=\"%s\">Go to this '
                                       'profile_point</a> or <a href="%s">all '
                                       'profile_points</a>.</div>') %
                                      (reverse('crits.profile_points.views.profile_point',
                                               args=[result['objectid']]),
                                       reverse('crits.profile_points.views.profile_points_listing')))

                    if result.get('is_new_profile_point', False) == False:
                        message = {'message': ('<div>Warning: Updated existing'
                                               ' ProfilePoint!' + profile_point_link)}
                    else:
                        message = {'message': ('<div>ProfilePoint added '
                                               'successfully!' + profile_point_link)}
                else:
                    failed_msg = result['message'] + ' - '

        if result == None or not result['success']:
            failed_msg += ('<a href="%s"> Go to all profile_points</a></div>'
                           % reverse('crits.profile_points.views.profile_points_listing'))
            message = {'message': failed_msg, 'form': form.as_table()}
        elif result != None:
            message['success'] = result['success']

        if request.is_ajax():
            return HttpResponse(json.dumps(message),
                                content_type="application/json")
        else: #file upload
            return render_to_response('file_upload_response.html',
                                      {'response': json.dumps(message)},
                                      RequestContext(request))


@user_passes_test(user_can_view_data)
def add_update_activity(request, method, profile_point_id):
    """
    Add/update an profile_point's activity. Should be an AJAX POST.

    :param request: Django request object (Required)
    :type request: :class:`django.http.HttpRequest`
    :param method: Whether we are adding or updating.
    :type method: str ("add", "update")
    :param profile_point_id: The ObjectId of the profile_point to update.
    :type profile_point_id: str
    :returns: :class:`django.http.HttpResponse`
    """

    if request.method == "POST" and request.is_ajax():
        username = request.user.username
        form = ProfilePointActivityForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            add = {
                'start_date': data['start_date'] if data['start_date'] else '',
                'end_date': data['end_date'] if data['end_date'] else '',
                'description': data['description'],
            }
            if method == "add":
                add['date'] = datetime.datetime.now()
                result = activity_add(profile_point_id, add, username)
            else:
                date = datetime.datetime.strptime(data['date'],
                                                  settings.PY_DATETIME_FORMAT)
                date = date.replace(microsecond=date.microsecond/1000*1000)
                add['date'] = date
                result = activity_update(profile_point_id, add, username)
            if 'object' in result:
                result['html'] = render_to_string('profile_points_activity_row_widget.html',
                                                  {'activity': result['object'],
                                                   'admin': is_admin(username),
                                                   'profile_point_id': profile_point_id})
            return HttpResponse(json.dumps(result, default=json_handler),
                                content_type="application/json")
        else: #invalid form
            return HttpResponse(json.dumps({'success': False,
                                            'form': form.as_table()}),
                                content_type="application/json")
    return HttpResponse({})


@user_passes_test(user_can_view_data)
def remove_activity(request, profile_point_id):
    """
    Remove an profile_point's activity. Should be an AJAX POST.

    :param request: Django request object (Required)
    :type request: :class:`django.http.HttpRequest`
    :param profile_point_id: The ObjectId of the profile_point to update.
    :type profile_point_id: str
    :returns: :class:`django.http.HttpResponse`
    """

    if request.method == "POST" and request.is_ajax():
        analyst = request.user.username
        if is_admin(analyst):
            date = datetime.datetime.strptime(request.POST['key'],
                                              settings.PY_DATETIME_FORMAT)
            date = date.replace(microsecond=date.microsecond/1000*1000)
            result = activity_remove(profile_point_id, date, analyst)
            return HttpResponse(json.dumps(result),
                                content_type="application/json")
        else:
            error = "You do not have permission to remove this item."
            return render_to_response("error.html",
                                      {'error': error},
                                      RequestContext(request))
