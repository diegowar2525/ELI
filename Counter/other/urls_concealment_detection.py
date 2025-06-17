from django.urls import path
from ..views import concealment_detection_views as views

urlpatterns = [
    path("", views.concealment_detection_view, name="concealment_detection"),
]
