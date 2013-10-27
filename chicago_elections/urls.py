from django.conf.urls import patterns, include, url
from .views import ballots_by_id

urlpatterns = patterns('',
    url(r'^ballots/(?P<election_id>\d+)/$', ballots_by_id),
)
