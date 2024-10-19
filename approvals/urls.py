from django.urls import path
from . import views

urlpatterns = [
    path("Approve", views.Approval.as_view(), name="Approval"),
    path("Approve/<str:pk>/", views.ApproveDetails.as_view(), name="ApproveDetails"),
    path(
        "ApprovalLeaveReliever/<str:pk>/",
        views.ApprovalLeaveReliever.as_view(),
        name="ApprovalLeaveReliever",
    ),
    path(
        "FnActionApprovals/<str:pk>/",
        views.FnActionApprovals.as_view(),
        name="FnActionApprovals",
    ),
]
