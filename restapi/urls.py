from django.urls import path
from . import rest_views, views

urlpatterns = [
    path('', views.api_overview, name='api-overview'),
    path('demo/', rest_views.HelloView.as_view(), name='hello_world'),
]
