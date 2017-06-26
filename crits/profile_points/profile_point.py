import datetime

from mongoengine import Document, StringField, ListField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField
from django.conf import settings

from crits.core.crits_mongoengine import CritsDocumentFormatter
from crits.core.crits_mongoengine import CritsBaseAttributes
from crits.core.crits_mongoengine import CritsSourceDocument
from crits.core.crits_mongoengine import CritsActionsDocument
from crits.core.fields import CritsDateTimeField


class EmbeddedActivity(EmbeddedDocument, CritsDocumentFormatter):
    """
    Indicator activity class.
    """

    analyst = StringField()
    end_date = CritsDateTimeField(default=datetime.datetime.now)
    date = CritsDateTimeField(default=datetime.datetime.now)
    description = StringField()
    start_date = CritsDateTimeField(default=datetime.datetime.now)


class ProfilePoint(CritsBaseAttributes, CritsSourceDocument,
                   CritsActionsDocument, Document):
    """
    Backdoor class.
    """

    meta = {
        "collection": settings.COL_PROFILE_POINTS,
        "crits_type": 'ProfilePoint',
        "latest_schema_version": 1,
        "schema_doc": {
            'value': 'The value of this profile point',
            'lower': 'The lowered value of this profile point',
            'description': 'The description for this profile point',
            'created': 'The ISODate when this profile point was entered',
            'modified': 'The ISODate when this profile point was last '
                        'modified',
            'activity': 'List [] of activity containing this profile point',
            'campaign': 'List [] of campaigns using this profile point',
            'source': ('List [] of source information about who provided this'
                       ' profile point')
        },
        "jtable_opts": {
            'details_url': 'crits.profile_points.views.profile_point_detail',
            'details_url_key': 'id',
            'default_sort': "modified DESC",
            'searchurl': 'crits.profile_points.views.profile_points_listing',
            'fields': ["value", "modified", "source",
                       "campaign", "status", "id"],
            'jtopts_fields': ["details", "value", "modified", "source",
                              "campaign", "status", "favorite", "id"],
            'hidden_fields': [],
            'linked_fields': ["value", "source", "campaign", "status"],
            'details_link': 'details',
            'no_sort': ['details'],
        }
    }

    value = StringField(required=True)
    lower = StringField()
    activity = ListField(EmbeddedDocumentField(EmbeddedActivity))

    def migrate(self):
        pass

    def add_activity(self, analyst, start_date, end_date,
                     description, date=None):
        """
        Add activity to an profile point.

        :param analyst: The user adding this activity.
        :type analyst: str
        :param start_date: The date this activity started.
        :type start_date: datetime.datetime
        :param end_date: The date this activity ended.
        :type end_date: datetime.datetime
        :param description: Description of the activity.
        :type description: str
        :param date: The date this activity was entered into CRITs.
        :type date: datetime.datetime
        """

        ea = EmbeddedActivity()
        ea.analyst = analyst
        ea.start_date = start_date
        ea.end_date = end_date
        ea.description = description
        if date:
            ea.date = date
        self.activity.append(ea)

    def edit_activity(self, analyst, start_date, end_date, description,
                      date=None):
        """
        Edit activity for an profile point.

        :param analyst: The user editing this activity.
        :type analyst: str
        :param start_date: The date this activity started.
        :type start_date: datetime.datetime
        :param end_date: The date this activity ended.
        :type end_date: datetime.datetime
        :param description: Description of the activity.
        :type description: str
        :param date: The date this activity was entered into CRITs.
        :type date: datetime.datetime
        """

        if not date:
            return
        for t in self.activity:
            if t.date == date:
                self.activity.remove(t)
                ea = EmbeddedActivity()
                ea.analyst = analyst
                ea.start_date = start_date
                ea.end_date = end_date
                ea.date = date
                ea.description = description
                self.activity.append(ea)
                break

    def delete_activity(self, date=None):
        """
        Delete activity from this profile point.

        :param date: The date of the activity entry to delete.
        :type date: datetime.datetime
        """

        if not date:
            return
        for t in self.activity:
            if t.date == date:
                self.activity.remove(t)
                break

