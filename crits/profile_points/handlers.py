import csv
import datetime
import json
import logging

from io import BytesIO
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
try:
    from mongoengine.base import ValidationError
except ImportError:
    from mongoengine.errors import ValidationError

from crits.campaigns.forms import CampaignForm
from crits.campaigns.campaign import Campaign
from crits.core import form_consts
from crits.core.class_mapper import class_from_id
from crits.core.crits_mongoengine import EmbeddedSource, EmbeddedCampaign
from crits.core.crits_mongoengine import json_handler
from crits.core.forms import SourceForm, DownloadFileForm
from crits.core.handlers import build_jtable, csv_export, action_add
from crits.core.handlers import jtable_ajax_list, jtable_ajax_delete
from crits.core.handlers import datetime_parser
from crits.core.user_tools import is_admin, user_sources
from crits.core.user_tools import is_user_subscribed, is_user_favorite
from crits.profile_points.forms import ProfilePointActivityForm
from crits.profile_points.profile_point import ProfilePoint
from crits.notifications.handlers import remove_user_from_notification
from crits.services.handlers import run_triage, get_supported_services
from crits.vocabulary.status import Status

logger = logging.getLogger(__name__)


def generate_profile_point_csv(request):
    """
    Generate a CSV file of the ProfilePoint information

    :param request: The request for this CSV.
    :type request: :class:`django.http.HttpRequest`
    :returns: :class:`django.http.HttpResponse`
    """

    response = csv_export(request, ProfilePoint)
    return response


def generate_profile_point_jtable(request, option):
    """
    Generate the jtable data for rendering in the list template.

    :param request: The request for this jtable.
    :type request: :class:`django.http.HttpRequest`
    :param option: Action to take.
    :type option: str of either 'jtlist', 'jtdelete', or 'inline'.
    :returns: :class:`django.http.HttpResponse`
    """

    obj_type = ProfilePoint
    type_ = "profile_point"
    mapper = obj_type._meta['jtable_opts']
    if option == "jtlist":
        # Sets display url
        details_url = mapper['details_url']
        details_url_key = mapper['details_url_key']
        fields = mapper['fields']
        response = jtable_ajax_list(obj_type,
                                    details_url,
                                    details_url_key,
                                    request,
                                    includes=fields)
        return HttpResponse(json.dumps(response,
                                       default=json_handler),
                            content_type="application/json")
    if option == "jtdelete":
        response = {"Result": "ERROR"}
        if jtable_ajax_delete(obj_type, request):
            response = {"Result": "OK"}
        return HttpResponse(json.dumps(response,
                                       default=json_handler),
                            content_type="application/json")
    jtopts = {
        'title': "ProfilePoints",
        'default_sort': mapper['default_sort'],
        'listurl': reverse('crits.%ss.views.%ss_listing' % (type_,
                                                            type_),
                           args=('jtlist',)),
        'deleteurl': reverse('crits.%ss.views.%ss_listing' % (type_,
                                                              type_),
                             args=('jtdelete',)),
        'searchurl': reverse(mapper['searchurl']),
        'fields': list(mapper['jtopts_fields']),
        'hidden_fields': mapper['hidden_fields'],
        'linked_fields': mapper['linked_fields'],
        'details_link': mapper['details_link'],
        'no_sort': mapper['no_sort']
    }
    jtable = build_jtable(jtopts, request)
    jtable['toolbar'] = [
        {
            'tooltip': "'All ProfilePoints'",
            'text': "'All'",
            'click': "function () {$('#profile_point_listing').jtable('load', {'refresh': 'yes'});}",
            'cssClass': "'jtable-toolbar-center'",
        },
        {
            'tooltip': "'New ProfilePoints'",
            'text': "'New'",
            'click': "function () {$('#profile_point_listing').jtable('load', {'refresh': 'yes', 'status': 'New'});}",
            'cssClass': "'jtable-toolbar-center'",
        },
        {
            'tooltip': "'In Progress ProfilePoints'",
            'text': "'In Progress'",
            'click': "function () {$('#profile_point_listing').jtable('load', {'refresh': 'yes', 'status': 'In Progress'});}",
            'cssClass': "'jtable-toolbar-center'",
        },
        {
            'tooltip': "'Analyzed ProfilePoints'",
            'text': "'Analyzed'",
            'click': "function () {$('#profile_point_listing').jtable('load', {'refresh': 'yes', 'status': 'Analyzed'});}",
            'cssClass': "'jtable-toolbar-center'",
        },
        {
            'tooltip': "'Informational ProfilePoints'",
            'text': "'Informational'",
            'click': "function () {$('#profile_point_listing').jtable('load', {'refresh': 'yes', 'status': 'Informational'});}",
            'cssClass': "'jtable-toolbar-center'",
        },
        {
            'tooltip': "'Deprecated ProfilePoints'",
            'text': "'Deprecated'",
            'click': "function () {$('#profile_point_listing').jtable('load', {'refresh': 'yes', 'status': 'Deprecated'});}",
            'cssClass': "'jtable-toolbar-center'",
        },
        {
            'tooltip': "'Add ProfilePoint'",
            'text': "'Add ProfilePoint'",
            'click': "function () {$('#new-profile_point').click()}",
        },
    ]
    if option == "inline":
        return render_to_response("jtable.html",
                                  {'jtable': jtable,
                                   'jtid': '%s_listing' % type_,
                                   'button': '%ss_tab' % type_},
                                  RequestContext(request))
    else:
        return render_to_response("%s_listing.html" % type_,
                                  {'jtable': jtable,
                                   'jtid': '%s_listing' % type_},
                                  RequestContext(request))


def get_profile_point_details(profile_point_id, analyst):
    """
    Generate the data to render the ProfilePoint details template.

    :param profile_point_id: The ObjectId of the ProfilePoint to get details for.
    :type profile_point_id: str
    :param analyst: The user requesting this information.
    :type analyst: str
    :returns: template (str), arguments (dict)
    """

    template = None
    users_sources = user_sources(analyst)
    profile_point = ProfilePoint.objects(id=profile_point_id,
                                         source__name__in=users_sources).first()
    if not profile_point:
        error = ("Either this profile_point does not exist or you do "
                 "not have permission to view it.")
        template = "error.html"
        args = {'error': error}
        return template, args
    forms = {}
    forms['new_activity'] = ProfilePointActivityForm(initial={'analyst': analyst,
                                                           'date': datetime.datetime.now()})
    forms['new_campaign'] = CampaignForm()#'date': datetime.datetime.now(),
    forms['new_source'] = SourceForm(analyst, initial={'date': datetime.datetime.now()})
    forms['download_form'] = DownloadFileForm(initial={"obj_type": 'ProfilePoint',
                                                       "obj_id": profile_point_id})

    profile_point.sanitize("%s" % analyst)

    # remove pending notifications for user
    remove_user_from_notification("%s" % analyst, profile_point_id, 'ProfilePoint')

    # subscription
    subscription = {
        'type': 'ProfilePoint',
        'id': profile_point_id,
        'subscribed': is_user_subscribed("%s" % analyst,
                                         'ProfilePoint',
                                         profile_point_id),
    }

    # relationship
    relationship = {
        'type': 'ProfilePoint',
        'value': profile_point_id,
    }

    # objects
    objects = profile_point.sort_objects()

    # relationships
    relationships = profile_point.sort_relationships("%s" % analyst, meta=True)

    # comments
    comments = {'comments': profile_point.get_comments(),
                'url_key': profile_point_id}

    # screenshots
    screenshots = profile_point.get_screenshots(analyst)

    # favorites
    favorite = is_user_favorite("%s" % analyst, 'ProfilePoint', profile_point.id)

    # services
    service_list = get_supported_services('ProfilePoint')

    # analysis results
    service_results = profile_point.get_analysis_results()

    args = {'objects': objects,
            'relationships': relationships,
            'comments': comments,
            'relationship': relationship,
            'subscription': subscription,
            "profile_point": profile_point,
            "forms": forms,
            "profile_point_id": profile_point_id,
            'screenshots': screenshots,
            'service_list': service_list,
            'service_results': service_results,
            'favorite': favorite,
            'rt_url': settings.RT_URL}

    return template, args


def get_verified_field(data, valid_values, field=None, default=None):
    """
    Validate and correct string value(s) in a dictionary key or list,
    or a string by itself.

    :param data: The data to be verified and corrected.
    :type data: dict, list of strings, or str
    :param valid_values: Key with simplified string, value with actual string
    :type valid_values: dict
    :param field: The dictionary key containing the data.
    :type field: str
    :param default: A value to use if an invalid item cannot be corrected
    :type default: str
    :returns: the validated/corrected value(str), list of values(list) or ''
    """

    if isinstance(data, dict):
        data = data.get(field, '')
    if isinstance(data, list):
        value_list = data
    else:
        value_list = [data]
    for i, item in enumerate(value_list):
        if isinstance(item, basestring):
            item = item.lower().strip().replace(' - ', '-')
            if item in valid_values:
                value_list[i] = valid_values[item]
                continue
        if default is not None:
            item = default
            continue
        return ''
    if isinstance(data, list):
        return value_list
    else:
        return value_list[0]


def handle_profile_point_csv(csv_data, source, method, reference, ctype,
                             username, add_domain=False, related_id=None,
                             related_type=None, relationship_type=None):
    """
    Handle adding ProfilePoints in CSV format (file or blob).

    :param csv_data: The CSV data.
    :type csv_data: str or file handle
    :param source: The name of the source for these profile_points.
    :type source: str
    :param method: The method of acquisition of this profile_point.
    :type method: str
    :param reference: The reference to this data.
    :type reference: str
    :param ctype: The CSV type.
    :type ctype: str ("file" or "blob")
    :param username: The user adding these profile_points.
    :type username: str
    :returns: dict with keys "success" (boolean) and "message" (str)
    """

    if ctype == "file":
        cdata = csv_data.read()
    else:
        cdata = csv_data.encode('ascii')
    data = csv.DictReader(BytesIO(cdata), skipinitialspace=True)
    result = {'success': True}
    result_message = ""
    # Compute permitted values in CSV
    valid_campaign_confidence = {
        'low': 'low',
        'medium': 'medium',
        'high': 'high'}
    valid_campaigns = {}
    for c in Campaign.objects(active='on'):
        valid_campaigns[c['name'].lower().replace(' - ', '-')] = c['name']

    # Start line-by-line import
    msg = "Cannot process row %s: %s<br />"
    added = 0
    for processed, d in enumerate(data, 1):
        pp = {}
        pp['value'] = (d.get('ProfilePoint') or '').strip()
        pp['lower'] = (d.get('ProfilePoint') or '').lower().strip()

        pp['status'] = d.get('Status', Status.NEW)
        if not pp['value']:
            # Mandatory value missing or malformed, cannot process csv row
            i = ""
            result['success'] = False
            if not pp['value']:
                i += "No valid ProfilePoint value "
            result_message += msg % (processed + 1, i)
            continue
        campaign = get_verified_field(d, valid_campaigns, 'Campaign')
        if campaign:
            pp['campaign'] = campaign
            pp['campaign_confidence'] = get_verified_field(d,
                                            valid_campaign_confidence,
                                            'Campaign Confidence',
                                            default='low')
        pp[form_consts.Common.BUCKET_LIST_VARIABLE_NAME] = d.get(form_consts.Common.BUCKET_LIST, '')
        pp[form_consts.Common.TICKET_VARIABLE_NAME] = d.get(form_consts.Common.TICKET, '')
        try:
            response = handle_profile_point_insert(pp, source, reference,
                                               analyst=username, method=method)
        except Exception as e:
            result['success'] = False
            result_message += msg % (processed + 1, e)
            continue
        if response['success']:
            if actions:
                action = {'active': 'on',
                          'analyst': username,
                          'begin_date': '',
                          'end_date': '',
                          'performed_date': '',
                          'reason': '',
                          'date': datetime.datetime.now()}
                for action_type in actions:
                    action['action_type'] = action_type
                    action_add('ProfilePoint', response.get('objectid'),
                               action, user=username)
        else:
            result['success'] = False
            result_message += msg % (processed + 1, response['message'])
            continue
        added += 1
    if processed < 1:
        result['success'] = False
        result_message = "Could not find any valid CSV rows to parse!"
    result['message'] = "Successfully added %s ProfilePoint(s).<br />%s" % (added, result_message)
    return result


def handle_profile_point_ind(value, source, analyst, status=None, method='',
                             reference='', campaign=None,
                             campaign_confidence=None, bucket_list=None,
                             ticket=None, cache={}):
    """
    Handle adding an individual profile_point.

    :param value: The profile_point value.
    :type value: str
    :param source: The name of the source for this profile_point.
    :type source: str
    :param analyst: The user adding this profile_point.
    :type analyst: str
    :param method: The method of acquisition of this profile_point.
    :type method: str
    :param reference: The reference to this data.
    :type reference: str
    :param campaign: Campaign to attribute to this profile_point.
    :type campaign: str
    :param campaign_confidence: Confidence of this campaign.
    :type campaign_confidence: str
    :param bucket_list: The bucket(s) to assign to this profile_point.
    :type bucket_list: str
    :param ticket: Ticket to associate with this profile_point.
    :type ticket: str
    :param cache: Cached data, typically for performance enhancements
                  during bulk uperations.
    :type cache: dict
    """

    result = None

    if not source:
        return {"success": False, "message": "Missing source information."}

    if status is None:
        status = Status.NEW

    if value is None or value.strip() == "":
        result = {'success': False,
                  'message': "Can't create profile_point with an empty value "
                             "field"}
    else:
        pp = {}
        pp['value'] = value.strip()
        pp['lower'] = value.lower().strip()
        pp['status'] = status

        if campaign:
            pp['campaign'] = campaign
        if campaign_confidence and campaign_confidence in ('low', 'medium', 'high'):
            pp['campaign_confidence'] = campaign_confidence
        if bucket_list:
            pp[form_consts.Common.BUCKET_LIST_VARIABLE_NAME] = bucket_list
        if ticket:
            pp[form_consts.Common.TICKET_VARIABLE_NAME] = ticket

        try:
            return handle_profile_point_insert(pp, source, reference, analyst,
                                               method, cache=cache)
        except Exception as e:
            return {'success': False, 'message': repr(e)}

    return result


def handle_profile_point_insert(pp, source, reference='', analyst='',
                                method='', cache={}):
    """
    Insert an individual profile_point into the database.

    :param pp: Information about the profile_point.
    :type pp: dict
    :param source: The source for this profile_point.
    :type source: list, str, :class:`crits.core.crits_mongoengine.EmbeddedSource`
    :param reference: The reference to the data.
    :type reference: str
    :param analyst: The user adding this profile_point.
    :type analyst: str
    :param method: Method of acquiring this profile_point.
    :type method: str
    :param cache: Cached data, typically for performance enhancements
                  during bulk uperations.
    :type cache: dict
    :returns: dict with keys:
              "success" (boolean),
              "message" (str) if failed,
              "objectid" (str) if successful,
              "is_new_profile_point" (boolean) if successful.
    """

    is_new_profile_point = False
    if pp.get('status', None) is None or len(pp.get('status', '')) < 1:
        pp['status'] = Status.NEW

    profile_point = ProfilePoint.objects(pp_type=pp['type'],
                                  lower=pp['lower']).first()

    if not profile_point:
        profile_point = ProfilePoint()
        profile_point.value = pp.get('value')
        profile_point.lower = pp.get('lower')
        profile_point.created = datetime.datetime.now()
        profile_point.status = pp.get('status')
        is_new_profile_point = True
    else:
        if pp['status'] != Status.NEW:
            profile_point.status = pp['status']

    if 'campaign' in pp:
        if isinstance(pp['campaign'], basestring) and len(pp['campaign']) > 0:
            confidence = pp.get('campaign_confidence', 'low')
            pp['campaign'] = EmbeddedCampaign(name=pp['campaign'],
                                              confidence=confidence,
                                              description="",
                                              analyst=analyst,
                                              date=datetime.datetime.now())
        if isinstance(pp['campaign'], EmbeddedCampaign):
            profile_point.add_campaign(pp['campaign'])
        elif isinstance(pp['campaign'], list):
            for campaign in pp['campaign']:
                if isinstance(campaign, EmbeddedCampaign):
                    profile_point.add_campaign(campaign)

    bucket_list = None
    if form_consts.Common.BUCKET_LIST_VARIABLE_NAME in pp:
        bucket_list = pp[form_consts.Common.BUCKET_LIST_VARIABLE_NAME]
        if bucket_list:
            profile_point.add_bucket_list(bucket_list, analyst)

    ticket = None
    if form_consts.Common.TICKET_VARIABLE_NAME in pp:
        ticket = pp[form_consts.Common.TICKET_VARIABLE_NAME]
        if ticket:
            profile_point.add_ticket(ticket, analyst)

    # generate new source information and add to profile_point
    if isinstance(source, basestring) and source:
        profile_point.add_source(source=source, method=method,
                                 reference=reference, analyst=analyst)
    elif isinstance(source, EmbeddedSource):
        profile_point.add_source(source_item=source, method=method,
                                 reference=reference)
    elif isinstance(source, list):
        for s in source:
            if isinstance(s, EmbeddedSource):
                profile_point.add_source(source_item=s, method=method,
                                         reference=reference)

    profile_point.save(username=analyst)

    # run profile_point triage
    if is_new_profile_point:
        profile_point.reload()
        run_triage(profile_point, analyst)

    return {'success': True, 'objectid': str(profile_point.id),
            'is_new_profile_point': is_new_profile_point,
            'object': profile_point}


def does_profile_point_relationship_exist(value, profile_point_relationships):
    """
    Checks if the input field's values already have an profile_point
    by cross checking against the list of profile_point relationships. The
    input field already has an associated profile_point created if the input
    field's "type" exists.

    Args:
        field: The generic input field containing a type/value pair. This is
            checked against a list of profile_points relationships to see if a
            corresponding profile_point already exists. This field is generally
            from custom dictionaries such as from Django templates.
        profile_point_relationships: The list of profile_point relationships
            to cross reference the input field against.

    Returns:
        Returns true if the input field already has an profile_point associated
            with its values. Returns false otherwise.
    """

    if profile_point_relationships is not None:
        if value is not None:
            for profile_point_relationship in profile_point_relationships:

                if profile_point_relationship is None:
                    logger.error('ProfilePoint relationship is not valid: ' +
                                 str(profile_point_relationship))
                    continue

                if value == profile_point_relationship.get('pp_value'):
                    return True
        else:
            logger.error('Could not extract value of input field '
                         'value: ' + (value.encode("utf-8") if value else str(value)) +
                         'profile_point_relationships: ' + str(profile_point_relationships))

    return False


def profile_point_remove(_id, username):
    """
    Remove an ProfilePoint from CRITs.

    :param _id: The ObjectId of the profile_point to remove.
    :type _id: str
    :param username: The user removing the profile_point.
    :type username: str
    :returns: dict with keys "success" (boolean) and "message" (list) if failed.
    """

    if is_admin(username):
        profile_point = ProfilePoint.objects(id=_id).first()
        if profile_point:
            profile_point.delete(username=username)
            return {'success': True}
        else:
            return {'success': False, 'message': ['Cannot find ProfilePoint']}
    else:
        return {'success': False, 'message': ['Must be an admin to delete']}


def activity_add(id_, activity, user, **kwargs):
    """
    Add activity to an ProfilePoint.

    :param id_: The ObjectId of the profile_point to update.
    :type id_: str
    :param activity: The activity information.
    :type activity: dict
    :param user: The user adding the activitty.
    :type user: str
    :returns: dict with keys:
              "success" (boolean),
              "message" (str) if failed,
              "object" (dict) if successful.
    """

    sources = user_sources(user)
    profile_point = ProfilePoint.objects(id=id_,
                                         source__name__in=sources).first()
    if not profile_point:
        return {'success': False,
                'message': 'Could not find ProfilePoint'}
    try:

        activity['analyst'] = user
        profile_point.add_activity(activity['analyst'],
                                   activity['start_date'],
                                   activity['end_date'],
                                   activity['description'],
                                   activity['date'])
        profile_point.save(username=user)
        return {'success': True, 'object': activity,
                'id': str(profile_point.id)}
    except ValidationError as e:
        return {'success': False, 'message': e,
                'id': str(profile_point.id)}


def activity_update(id_, activity, user=None, **kwargs):
    """
    Update activity for an ProfilePoint.

    :param id_: The ObjectId of the profile_point to update.
    :type id_: str
    :param activity: The activity information.
    :type activity: dict
    :param user: The user updating the activity.
    :type user: str
    :returns: dict with keys:
              "success" (boolean),
              "message" (str) if failed,
              "object" (dict) if successful.
    """

    sources = user_sources(user)
    profile_point = ProfilePoint.objects(id=id_,
                                         source__name__in=sources).first()
    if not profile_point:
        return {'success': False,
                'message': 'Could not find ProfilePoint'}
    try:
        activity = datetime_parser(activity)
        activity['analyst'] = user
        profile_point.edit_activity(activity['analyst'],
                                    activity['start_date'],
                                    activity['end_date'],
                                    activity['description'],
                                    activity['date'])
        profile_point.save(username=user)
        return {'success': True, 'object': activity}
    except ValidationError as e:
        return {'success': False, 'message': e}


def activity_remove(id_, date, user, **kwargs):
    """
    Remove activity from an ProfilePoint.

    :param id_: The ObjectId of the profile_point to update.
    :type id_: str
    :param date: The date of the activity to remove.
    :type date: datetime.datetime
    :param user: The user removing this activity.
    :type user: str
    :returns: dict with keys "success" (boolean) and "message" (str) if failed.
    """

    profile_point = ProfilePoint.objects(id=id_).first()
    if not profile_point:
        return {'success': False,
                'message': 'Could not find ProfilePoint'}
    try:

        date = datetime_parser(date)
        profile_point.delete_activity(date)
        profile_point.save(username=user)
        return {'success': True}
    except ValidationError as e:
        return {'success': False, 'message': e}
