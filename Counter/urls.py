from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("panel/", views.panel_view, name="panel"),
    path("upload/", views.upload_view, name="upload"),
    path("totalcount/", views.totalcount_view, name="totalcount"),
    path("companies/", include("Counter.urls_company")),
    path("reports/", include("Counter.urls_report")),
    path("expert_lists/", views.expert_lists_view, name="expert_lists"),
    path("concealment_detection/", views.concealment_detection_view, name="concealment_detection"),
    path("comparative_analysis/", views.comparative_analysis_view, name="comparative_analysis"),
    path("users/", views.users_view, name="users"),
]

