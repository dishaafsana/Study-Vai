from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("quiz/", views.quiz, name="quiz"),
    # AI-Powered Quiz API Endpoints
    path(
        "api/quiz/generate-questions/", views.generate_quiz_questions, name="api_generate_questions"
    ),
    path(
        "api/quiz/generate-explanation/",
        views.generate_explanation,
        name="api_generate_explanation",
    ),
    path(
        "api/quiz/generate-assessment/",
        views.generate_performance_assessment,
        name="api_generate_assessment",
    ),
    # Other app urls
    path("", include("users.urls")),
    path("", include("Groups.urls")),
    path("", include("notes.urls")),
    path("", include("routine.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
