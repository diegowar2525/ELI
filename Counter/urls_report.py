from django.urls import path
from . import views

urlpatterns = [
    path("", views.reports_view, name="reports"),
    path("<int:report_id>/json/", views.see_report_json, name="see_report_json"),
    path("<int:report_id>/delete/", views.delete_report, name="delete_report"),
    path("<int:report_id>/update/", views.update_report, name="update_report"),
    path('<int:report_id>/report_count/', views.totalcountreport_view, name='report_count')
]
