from django.urls import path
from . import views

urlpatterns = [
    path("Documentation/", views.Documentation.as_view(), name="Documentation"),
]
