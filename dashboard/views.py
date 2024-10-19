import asyncio
import base64
import logging
import aiohttp
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from myRequest.views import UserObjectMixins
from django.contrib import messages
from asgiref.sync import sync_to_async
from django.conf import settings as config
from datetime import datetime
import json as jsons
import base64
from django.http import HttpResponse


class Dashboard(UserObjectMixins, View):
    async def get(self, request):
        try:
            UserId = await sync_to_async(request.session.__getitem__)("User_ID")
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            open_leave_applications = ""
            if open_leave_count > 0:
                open_leave_applications = await sync_to_async(
                    request.session.__getitem__
                )("open_leave_applications")
            openLeave = []
            approvedLeave = []
            Rejected = []
            pendingLeave = []
            Document_Types = [
                "19",
                "20",
            ]

            async with aiohttp.ClientSession() as session:
                task_get_leave = asyncio.ensure_future(
                    self.fetch_one_filtered_data(
                        session, "/QyLeaveApplications", "User_ID", "eq", UserId
                    )
                )
                task_open_approvals = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", UserId
                    )
                )
                response = await asyncio.gather(task_get_leave, task_open_approvals)

                openLeave = [x for x in response[0]["data"] if x["Status"] == "Open"]
                pendingLeave = [
                    x for x in response[0]["data"] if x["Status"] == "Pending Approval"
                ]
                approvedLeave = [
                    x for x in response[0]["data"] if x["Status"] == "Released"
                ]
                Rejected = [x for x in response[0]["data"] if x["Status"] == "Rejected"]
                open_approvals = [
                    x
                    for x in response[1]
                    if x["Status"] == "Open" and x["DocumentType"] in Document_Types
                ]

        except Exception as e:
            messages.info(request, f"{e}")
            return redirect("dashboard")
        ctx = {
            "res": openLeave,
            "response": approvedLeave,
            "rejected": Rejected,
            "pending": pendingLeave,
            "username": full_name,
            "open_approvals": open_approvals,
            "open_leave_count": open_leave_count,
            "open_leave_applications": open_leave_applications,
            "Employee": Employee,
        }
        return render(request, "dashboard.html", ctx)


class FnGetAnnualLeaveDashboard(UserObjectMixins, View):
    async def get(self, request):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            Employee_No_ = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )
            response = self.make_soap_request(
                soap_headers, "FnGetAnnualLeaveDashboard", Employee_No_, 0, 0, 0, 0, 0
            )

            response_dict = {
                "availableMaxOverdraft": float(response.availableMaxOverdraft),
                "leaveEarnedToDate": float(response.leaveEarnedToDate),
                "balanceBF": float(response.balanceBF),
                "daysTakenToDate": float(response.daysTakenToDate),
                "recalledDays": float(response.recalledDays),
            }

            sorted_data = jsons.dumps(response_dict, indent=3)

            return JsonResponse(response_dict, safe=False)
        except Exception as e:
            logging.exception(e)
            return JsonResponse(str(e), safe=False)
