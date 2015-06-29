from django.conf.urls import patterns

urlpatterns = patterns('crits.vis.views',
    (r'(?P<object_id>\w+)/$', 'vis_graph'),
)
