from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path("learner/", views.learner, name="learner"),
    path("TeamLeader/", views.TeamLeader, name="TeamLeader"),
    path("contact/", views.contact, name="contact"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("student-profile/", views.student_profile, name="student_profile"),
    path("TeamLeader-profile/", views.TeamLeader_profile, name="TeamLeader_profile"),
    path("student-marks/", views.student_marks, name="student_marks"),
    path("TeamLeader-class-call/", views.TeamLeader_class_call, name="TeamLeader_class_call"),
    path("student-profile/edit/", views.edit_student_profile, name="edit_student_profile"),
    path("TeamLeader-profile/edit/", views.edit_TeamLeader_profile, name="edit_TeamLeader_profile"),
    # Other URLs
]
