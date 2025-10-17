from django.urls import path
from . import views

urlpatterns = [
    path("Groups/", views.Groups, name="Groups"),
    path("Groups/<int:pk>/", views.Group_detail, name="Group_detail"),
    path("Groups/<int:pk>/update/", views.update_Group, name="update_Group"),
    path("Groups/<int:pk>/delete/", views.delete_Group, name="delete_Group"),
    path("add/", views.add_Group, name="add_Group"),
    path("Groups/<int:pk>/join/", views.join_group, name="join_group"),
]
