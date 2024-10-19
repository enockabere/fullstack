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
import datetime
import io as BytesIO
import base64
from django.http import HttpResponse


# Create your views here.
class Approval(UserObjectMixins, View):
    async def get(self, request):
        try:
            ctx = {}
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            User_ID = await sync_to_async(request.session.__getitem__)("User_ID")
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            open_leave_applications = ""
            if open_leave_count > 0:
                open_leave_applications = await sync_to_async(
                    request.session.__getitem__
                )("open_leave_applications")
            Document_Types = [
                "18",
                "20",
                "25",
            ]
            async with aiohttp.ClientSession() as session:
                task_open_approvals = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", User_ID
                    )
                )
                response = await asyncio.gather(task_open_approvals)

                open_approvals = [
                    x
                    for x in response[0]
                    if x["Status"] == "Open" and x["DocumentType"] in Document_Types
                ]
                closed_approvals = [
                    x
                    for x in response[0]
                    if x["Status"] == "Approved" and x["DocumentType"] in Document_Types
                ]
                rejected_approvals = [
                    x
                    for x in response[0]
                    if x["Status"] == "Rejected" and x["DocumentType"] in Document_Types
                ]
                ctx = {
                    "open_approvals": open_approvals,
                    "closed_approvals": closed_approvals,
                    "rejected_approvals": rejected_approvals,
                    "username": full_name,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                    "Employee": Employee,
                }
        except Exception as e:
            logging.exception(e)
            current_url = request.get_full_path()
            request.session["saved_url"] = current_url
            messages.info(request, "session created")
            return redirect("sign_in")
        return render(request, "approve.html", ctx)


class ApproveDetails(UserObjectMixins, View):
    async def get(self, request, pk):
        try:
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            Department = await sync_to_async(request.session.__getitem__)("Department")
            User_ID = await sync_to_async(request.session.__getitem__)("User_ID")
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            open_leave_applications = ""
            if open_leave_count > 0:
                open_leave_applications = await sync_to_async(
                    request.session.__getitem__
                )("open_leave_applications")
            data = []
            res = {}
            relievers = []
            leave_applicant = None
            Document_Types = [
                "18",
                "20",
                "25",
            ]

            if "&" in Department:
                Department = Department.replace("&", "%26")

            async with aiohttp.ClientSession() as session:
                task1 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "DocumentNo", "eq", pk
                    )
                )
                task2 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyDocumentAttachments", "No", "eq", pk
                    )
                )
                task3 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveApplications", "Application_No", "eq", pk
                    )
                )

                task4 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session,
                        "/QyEmployees",
                        "Global_Dimension_2_Code",
                        "eq",
                        Department,
                    )
                )
                task5 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", User_ID
                    )
                )
                task6 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveRelievers", "LeaveCode", "eq", pk
                    )
                )
                task7 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveAdjustmentHeader", "Code", "eq", pk
                    )
                )
                task8 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveAdjustmentLines", "HeaderNo", "eq", pk
                    )
                )
                task9 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveApplications", "Status", "eq", "Released"
                    )
                )
                task10 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveRecalls", "No", "eq", pk
                    )
                )
                response = await asyncio.gather(
                    task1,
                    task2,
                    task3,
                    task4,
                    task5,
                    task6,
                    task7,
                    task8,
                    task9,
                    task10,
                )

                for document in response[0]:
                    if document["ApproverID"] == User_ID:
                        res = document
                allFiles = [x for x in response[1]]

                for leave in response[2]:
                    data = leave
                    leave_applicant = leave["Employee_No"]
                for adjustment in response[6]:
                    data = adjustment

                for recall in response[9]:
                    data = recall

                if Department == "None":
                    relievers = []
                else:
                    relievers = [x for x in response[3] if x["No_"] != leave_applicant]

                employees = [x for x in response[3]]

                user_ids = [employee["User_ID"] for employee in employees]

                department_leave = [x for x in response[8] if x["User_ID"] in user_ids]

                today = datetime.date.today()

                future_department_leave = [
                    x
                    for x in department_leave
                    if datetime.datetime.strptime(
                        x["Resumption_Date"], "%Y-%m-%d"
                    ).date()
                    > today
                ]

                open_approvals = [
                    x
                    for x in response[4]
                    if x["Status"] == "Open" and x["DocumentType"] in Document_Types
                ]

                Relievers = [x for x in response[5]]

                adjustmentLine = [x for x in response[7] if x["HeaderNo"] == pk]

                ctx = {
                    "res": res,
                    "file": allFiles,
                    "data": data,
                    "username": full_name,
                    "relievers": relievers,
                    "open_approvals": open_approvals,
                    "Relievers": Relievers,
                    "department_leave": future_department_leave,
                    "Department": Department,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                    "Employee": Employee,
                    "adjustmentLine": adjustmentLine,
                }
        except Exception as e:
            logging.exception(e)
            current_url = request.get_full_path()
            request.session["saved_url"] = current_url
            messages.info(request, "session created")
            return redirect("sign_in")
        return render(request, "approveDetails.html", ctx)


class ApprovalLeaveReliever(UserObjectMixins, View):
    def post(self, request, pk):
        try:
            soap_headers = request.session["soap_headers"]
            reliever = request.POST.get("Reliever")
            response = self.make_soap_request(
                soap_headers, "FnLeaveReliever", pk, reliever
            )
            if response != "0" and response != None and response != "":
                messages.success(request, "Added Successfully")
                return redirect("ApproveDetails", pk=pk)
            messages.error(request, f"{response}")
            return redirect("ApproveDetails", pk=pk)
        except Exception as e:
            messages.error(request, f"{e}")
            print(e)
            return redirect("ApproveDetails", pk=pk)


class FnActionApprovals(UserObjectMixins, View):
    def post(self, request, pk):
        try:
            soap_headers = request.session["soap_headers"]
            tableID = int(request.POST.get("tableID"))
            entryNo = int(request.POST.get("entryNo"))
            statusApproveRejectDelegate = request.POST.get(
                "statusApproveRejectDelegate"
            )
            approvalComment = request.POST.get("approvalComment")
            User_ID = request.session["User_ID"]

            response = self.make_soap_request(
                soap_headers,
                "FnActionApprovals",
                tableID,
                pk,
                entryNo,
                statusApproveRejectDelegate,
                approvalComment,
                User_ID,
            )
            if response != "0" and response != None and response != "":
                messages.success(request, "Approved Successfully")
                return redirect("Approval")
            messages.error(request, f"{response}")
            return redirect("ApproveDetails", pk=pk)
        except Exception as e:
            messages.error(request, f"{e}")
            print(e)
            return redirect("ApproveDetails", pk=pk)
