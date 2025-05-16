from django.urls import path
from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("panel/", views.panel_view, name="panel"),
    path("companies/", views.companies_view, name="companies"),
    path("reports", views.reports_view, name="reports"),
    path("upload/", views.upload_view, name="upload"),
    path("totalcount/", views.totalcount_view, name="totalcount"),
    path("create_company/", views.create_company, name="create_company"),
    path('companies/<int:company_id>/json/', views.see_company_json, name='see_company_json'),
]
