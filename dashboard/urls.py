from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.Dashboard.as_view(), name="dashboard"),
    path(
        "FnGetAnnualLeaveDashboard/",
        views.FnGetAnnualLeaveDashboard.as_view(),
        name="FnGetAnnualLeaveDashboard",
    ),
]
