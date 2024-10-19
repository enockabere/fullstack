from django.urls import path
from . import views

urlpatterns = [
    path("Leave", views.NewLeave.as_view(), name="NewLeave"),
    path("Applications", views.Applications.as_view(), name="Applications"),
    path("Leave/<str:pk>/", views.LeaveDetails.as_view(), name="LeaveDetails"),
    path("LeaveApprove/<str:pk>", views.LeaveApproval.as_view(), name="LeaveApprove"),
    path(
        "LeaveCancel/<str:pk>", views.LeaveCancelApproval.as_view(), name="LeaveCancel"
    ),
    path(
        "FnLeaveReliever/<str:pk>/",
        views.FnLeaveReliever.as_view(),
        name="FnLeaveReliever",
    ),
    path(
        "FnArchiveLeaveApplication/<str:pk>/",
        views.FnArchiveLeaveApplication.as_view(),
        name="FnArchiveLeaveApplication",
    ),
    path(
        "DeleteLeaveAttachment/<str:pk>",
        views.DeleteLeaveAttachment.as_view(),
        name="DeleteLeaveAttachment",
    ),
    path(
        "FnGenerateLeave/<str:pk>",
        views.FnGenerateLeaveReport.as_view(),
        name="FnGenerateLeaveReport",
    ),
    path("LeaveReports", views.LeaveReports.as_view(), name="LeaveReports"),
    path("LeaveAdjustments", views.LeaveAdjustments.as_view(), name="LeaveAdjustments"),
    path("MyAdjustments", views.MyAdjustments.as_view(), name="MyAdjustments"),
    path(
        "Adjustment/<str:pk>/",
        views.AdjustmentDetails.as_view(),
        name="AdjustmentDetails",
    ),
    path(
        "FnRequestLeaveAdjustmentApproval/<str:pk>/",
        views.FnRequestLeaveAdjustmentApproval.as_view(),
        name="FnRequestLeaveAdjustmentApproval",
    ),
    path(
        "FnCancelLeaveAdjustmentApproval/<str:pk>/",
        views.FnCancelLeaveAdjustmentApproval.as_view(),
        name="FnCancelLeaveAdjustmentApproval",
    ),
    path("LeavePlanner/", views.LeavePlanner.as_view(), name="LeavePlanner"),
    path(
        "NumberOfDaysFilter/",
        views.NumberOfDaysFilter.as_view(),
        name="NumberOfDaysFilter",
    ),
    path(
        "FnLeavePlannerLine/<str:pk>/",
        views.FnLeavePlannerLine.as_view(),
        name="FnLeavePlannerLine",
    ),
    path(
        "FnReOpenLeavePlanner/<str:pk>/",
        views.FnReOpenLeavePlanner.as_view(),
        name="FnReOpenLeavePlanner",
    ),
    path(
        "FnSubmitLeavePlanner/<str:pk>/",
        views.FnSubmitLeavePlanner.as_view(),
        name="FnSubmitLeavePlanner",
    ),
    path("Plans", views.MyPlans.as_view(), name="MyPlans"),
    path(
        "Plan/<str:pk>/",
        views.PlannerDetails.as_view(),
        name="PlannerDetails",
    ),
    path("LeaveDashboard", views.LeaveDashboard.as_view(), name="LeaveDashboard"),
    path("LeaveBalance/", views.LeaveBalance.as_view(), name="LeaveBalance"),
]
