from django.conf.urls import url

urlpatterns = [
    url(r'^details/(?P<profile_point_id>\w+)/$', 'profile_point',
        prefix='crits.profile_points.views'),
    url(r'^search/$', 'profile_point_search',
        prefix='crits.profile_points.views'),
    url(r'^upload/$', 'upload_profile_point',
        prefix='crits.profile_points.views'),
    url(r'^remove/(?P<_id>[\S ]+)$', 'remove_profile_point',
        prefix='crits.profile_points.views'),
    url(r'^activity/remove/(?P<profile_point_id>\w+)/$', 'remove_activity',
        prefix='crits.profile_points.views'),
    url(r'^activity/(?P<method>\S+)/(?P<profile_point_id>\w+)/$',
        'add_update_activity', prefix='crits.profile_points.views'),
    url(r'^list/$', 'profile_points_listing',
        prefix='crits.profile_points.views'),
    url(r'^list/(?P<option>\S+)/$', 'profile_points_listing',
        prefix='crits.profile_points.views'),
]
