import json
import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from mongoengine.base import ValidationError

from crits.core import form_consts
from crits.core.crits_mongoengine import json_handler
from crits.core.crits_mongoengine import CritsBaseAttributes
from crits.core.handlers import jtable_ajax_list, build_jtable, jtable_ajax_delete
from crits.core.handlers import csv_export
from crits.core.user_tools import is_user_subscribed, user_sources
from crits.core.user_tools import is_user_favorite
from crits.emails.email import Email
from crits.events.event import Event
from crits.indicators.indicator import Indicator
from crits.samples.sample import Sample
from crits.ips.ip import IP
from crits.domains.domain import Domain
from crits.services.handlers import run_triage
from crits.relationships.handlers import get_relationships

logger = logging.getLogger(__name__)


def generate_vis_graph(analyst, start_id):
    """
    Generate data for the nodes and relationships for the vis.js graph.

    :param request: The request for this visualization.
    :type request: :class:`django.http.HttpRequest`
    :param object_id: The object_id that begins the graph analysis
    :type str
    :returns: :class:`django.http.HttpResponse`
    """
    sources = user_sources(analyst)
    obj = find_document(start_id, sources)
    if not obj:
        args = {'error': "ID does not exist or insufficient privs for source"}
        return ("error.html", args)

    vismap = { 'nodes' : [], 'edges' : [] }
    id_list = []
    vismap = build_relationships(obj, vismap, sources, 1, 30, id_list)

    return ("vis.html", vismap)


def build_relationships(obj, vismap, sources, cur_depth, max_depth, id_list):
    """
    Recursive function to build relationship mapping.

    :param obj: The object to recurse on
    :type obj: :class:`crits.core.crits_mongoengine.CritsBaseAttributes`
    :param vismap: The current mapping
    :type vismap: dict
    """
    id_list.append(str(obj.id))

    if obj.__class__.__name__ == "Indicator":
        label = obj.value
        shape = 'dot'
        size = 10
        color = '#00CCFF'
        color_border = '#007A99'
        color_highlight = '#66E0FF'
        color_highlight_border = '#00CCFF'

    elif obj.__class__.__name__ == "Event":
        label = obj.title
        shape = 'dot'
        size = 35
        color = '#00FF00'
        color_border = '#009900'
        color_highlight = '#66FF66'
        color_highlight_border = '#00FF00'

    elif obj.__class__.__name__ == "Sample":
        label = obj.filename
        shape = 'dot'
        size = 25 
        color = '#FF6666'
        color_border = '#993D3D'
        color_highlight = '#FFA3A3'
        color_highlight_border = '#FF6666'

    elif obj.__class__.__name__ == "Email":
        label = obj.subject
        shape = 'dot'
        size = 25
        color = '#CC66FF'
        color_border = '#7A3D99'
        color_highlight = '#E0A3FF'
        color_highlight_border = '#CC66FF'

    elif obj.__class__.__name__ == "Domain":
        label = obj.domain
        shape = 'dot'
        size = 20
        color = '#FF9933'
        color_border = '#995C1F'
        color_highlight = '#FFC285'
        color_highlight_border = '#FF9933'

    elif obj.__class__.__name__ == "IP":
        label = obj.ip
        shape = 'dot'
        size = 20
        color = '#FFFF66'
        color_border = '#99993D'
        color_highlight = '#FFFFA3'
        color_highlight_border = '#FFFF66'

    else:
        return vismap

    label = label.replace('\\', '\\\\')
    vismap['nodes'].append( { 'id' : '{0}'.format(obj.id), 'label' : label,
        'shape' : shape, 'size' : size, 'color' : color, 'color_border' :
        color_border, 'color_highlight_border' : color_highlight_border,
        'color_highlight' : color_highlight } )

    cur_depth += 1
    if cur_depth > max_depth:
        return vismap

    for rel in obj.relationships:
        new_obj = None
        if contains_edge(str(rel.object_id), str(obj.id), vismap):
            continue
        if rel.rel_type == "Indicator":
            new_obj = Indicator.objects(id=rel.object_id, source__name__in=sources).first()
            vismap['edges'].append( { 'from_id' : '{0}'.format(obj.id), 'to_id' :
                '{0}'.format(rel.object_id) } )
        if rel.rel_type == 'Event':
            new_obj = Event.objects(id=rel.object_id, source__name__in=sources).first()
            vismap['edges'].append( { 'from_id' : '{0}'.format(obj.id), 'to_id' :
                '{0}'.format(rel.object_id) } )
        if rel.rel_type == 'Email':
            new_obj = Email.objects(id=rel.object_id, source__name__in=sources).first()
            vismap['edges'].append( { 'from_id' : '{0}'.format(obj.id), 'to_id' :
                '{0}'.format(rel.object_id) } )
        if rel.rel_type == 'Sample':
            new_obj = Sample.objects(id=rel.object_id, source__name__in=sources).first()
            vismap['edges'].append( { 'from_id' : '{0}'.format(obj.id), 'to_id' :
                '{0}'.format(rel.object_id) } )
        if rel.rel_type == 'Domain':
            new_obj = Domain.objects(id=rel.object_id, source__name__in=sources).first()
            vismap['edges'].append( { 'from_id' : '{0}'.format(obj.id), 'to_id' :
                '{0}'.format(rel.object_id) } )
        if rel.rel_type == 'IP':
            new_obj = IP.objects(id=rel.object_id, source__name__in=sources).first()
            vismap['edges'].append( { 'from_id' : '{0}'.format(obj.id), 'to_id' :
                '{0}'.format(rel.object_id) } )

        if new_obj is not None:
            if str(new_obj.id) not in id_list:
                vismap = build_relationships(new_obj, vismap, sources, cur_depth,
                    max_depth, id_list)

    return vismap


def find_document(object_id, sources):
    doc = Indicator.objects(id=object_id, source__name__in=sources).first()
    if doc is not None:
        return doc
    doc = Event.objects(id=object_id, source__name__in=sources).first()
    if doc is not None:
        return doc
    doc = Email.objects(id=object_id, source__name__in=sources).first()
    if doc is not None:
        return doc
    doc = Sample.objects(id=object_id, source__name__in=sources).first()
    if doc is not None:
        return doc
    doc = Domain.objects(id=object_id, source__name__in=sources).first()
    if doc is not None:
        return doc
    doc = IP.objects(id=object_id, source__name__in=sources).first()
    if doc is not None:
        return doc


def contains_edge(id1, id2, vismap):
    for edge in vismap['edges']:
        if edge['from_id'] == id1 and edge['to_id'] == id2:
            return True
        if edge['from_id'] == id2 and edge['to_id'] == id1:
            return True
    return False
