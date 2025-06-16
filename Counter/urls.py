from django.urls import path, include
from .views import general_views as views

urlpatterns = [
    # Main views
    path("", views.index_view, name="index"),
    path("panel/", views.panel_view, name="panel"),
    path("upload/", views.upload_view, name="upload"),
    path("concealment_detection/", views.concealment_detection_view, name="concealment_detection"),
    path("comparative_analysis/", views.comparative_analysis_view, name="comparative_analysis"),
    path("users/", views.user_view, name="users"),

    # Included URLConfs
    path("totalcount/", include("Counter.other.urls_total_count")),
    path("companies/", include("Counter.other.urls_company")),
    path("reports/", include("Counter.other.urls_report")),
    path("expert_lists/", include("Counter.other.urls_expert_lists")),
]

