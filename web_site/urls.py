from django.conf.urls import url
from web_site import views

urlpatterns = [
    url(r'^$', views.SearchView.as_view(), name="search"),
    url(r'^save/$', views.SaveAccessorMarks.as_view(), name="save"),
    url(r'^documents/(?P<pk>\d+)/$', views.DocumentView.as_view(), name="document"),
    url(r'results/$', views.ResultPage.as_view(), name="result")
]
