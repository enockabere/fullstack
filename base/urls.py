from django.urls import path
from . import views

urlpatterns = [
    path("LeaveBalances", views.LeaveBalances.as_view(), name="LeaveBalances"),
    path("Profile/", views.Profile.as_view(), name="Profile"),
    path("Attachments/<str:pk>/", views.Attachments.as_view(), name="Attachments"),
    path("ApprovalRequest/", views.ApprovalRequest.as_view(), name="ApprovalRequest"),
    path("CancelApproval/", views.CancelApprovalForm.as_view(), name="CancelApproval"),
    path("filter_list/<str:pk>", views.filter_list.as_view(), name="filter_list"),
    path(
        "RemoveAttachment/", views.RemoveAttachment.as_view(), name="RemoveAttachment"
    ),
    path(
        "ApproversData/<str:pk>/", views.ApproversData.as_view(), name="ApproversData"
    ),
    path(
        "DownloadDocs/<str:pk>/<str:id>/",
        views.DownloadDocs.as_view(),
        name="DownloadDocs",
    ),
]
