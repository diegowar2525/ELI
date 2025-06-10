from django.urls import path
from . import views

urlpatterns = [
    path("", views.expert_lists_view, name="expert_lists"),
    path("create/", views.create_list, name="create_expert_list"),
    path("<int:list_id>/json/", views.get_list_json, name="get_list_json"),
    path("<int:list_id>/update/", views.update_list, name="update_expert_list"),
    path("<int:list_id>/delete/", views.delete_list, name="delete_expert_list"),
]


