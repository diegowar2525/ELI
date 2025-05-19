from django.urls import path
from . import views

urlpatterns = [
    path("", views.companies_view, name="companies"),
    path("<int:report_id>/json/", views.see_report_json, name="see_report_json"),

]
