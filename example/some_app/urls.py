from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', SomePageView.as_view(), name='some_page'),
    url(r'^redirect/$', RedirectView.as_view(), name='some_redirect'),

    url(r'^api/v1/some-api/$', SomeAPIView.as_view(), name='some_api'),
    url(r'^api/v1/user/list/$', UserListAPIView.as_view(), name='user_list'),
    url(
        r'^api/v1/user/(?P<pk>\d+)/update/$',
        UserRetrieveUpdateAPIView.as_view(),
        name='user_update'
    ),
]
