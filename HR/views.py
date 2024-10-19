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
from datetime import datetime as dates
import io as BytesIO
from django.http import HttpResponse
import datetime


class NewLeave(UserObjectMixins, View):
    async def get(self, request):
        try:
            UserId = await sync_to_async(request.session.__getitem__)("User_ID")
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            Department = await sync_to_async(request.session.__getitem__)("Department")
            employeeNo = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            open_leave_applications = ""
            if open_leave_count > 0:
                open_leave_applications = await sync_to_async(
                    request.session.__getitem__
                )("open_leave_applications")
            Document_Types = [
                "19",
                "20",
            ]

            if "&" in Department:
                Department = Department.replace("&", "%26")

            async with aiohttp.ClientSession() as session:
                task1 = asyncio.ensure_future(
                    self.simple_fetch_data(session, "/QyLeaveTypes")
                )
                task_get_relievers = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session,
                        "/QyEmployees",
                        "Global_Dimension_2_Code",
                        "eq",
                        Department,
                    )
                )
                task_approvals_count = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", UserId
                    )
                )
                task_planner = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeavePlanLines", "EmployeeNo", "eq", employeeNo
                    )
                )

                task_planner_header = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session,
                        "/QyLeavePlannerHeaders",
                        "Employee_No_",
                        "eq",
                        employeeNo,
                    )
                )

                response = await asyncio.gather(
                    task1,
                    task_get_relievers,
                    task_approvals_count,
                    task_planner,
                    task_planner_header,
                )
                LeaveTypes = [x for x in response[0]]
                relievers = [x for x in response[1] if x["No_"] != employeeNo]
                open_approvals = [
                    x
                    for x in response[2]
                    if x["Status"] == "Open" and x["DocumentType"] in Document_Types
                ]
                Plan_Header = [x for x in response[4] if x["Submitted"] == True]
                No_Values = [x["No_"] for x in Plan_Header]

                Plan_Lines = [x for x in response[3] if x["DocumentNo"] in No_Values]

        except Exception as e:
            messages.error(request, f"{e}")
            return redirect("dashboard")
        ctx = {
            "username": full_name,
            "leave": LeaveTypes,
            "Reliever": relievers,
            "open_approvals": open_approvals,
            "plan": Plan_Lines,
            "Plan_Header": Plan_Header,
            "open_leave_count": open_leave_count,
            "open_leave_applications": open_leave_applications,
            "Employee": Employee,
        }
        return render(request, "Leave/new_leave.html", ctx)

    async def post(self, request):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            applicationNo = request.POST.get("applicationNo")
            employeeNo = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )
            usersId = await sync_to_async(request.session.__getitem__)("User_ID")
            leaveType = request.POST.get("leaveType")
            BasedOnPlanner = eval(request.POST.get("usePlanner"))
            plannerStartDate = request.POST.get("plannerStartDate")
            LeaveStartDate = request.POST.get("LeaveStartDate")
            daysApplied = request.POST.get("daysApplied")
            isReturnSameDay = request.POST.get("isReturnSameDay")
            whichHalfOfDay = request.POST.get("whichHalfOfDay")
            myAction = request.POST.get("myAction")

            if BasedOnPlanner == True:
                plannerStartDate = dates.strptime(plannerStartDate, "%Y-%m-%d").date()
            else:
                plannerStartDate = dates.strptime(LeaveStartDate, "%Y-%m-%d").date()

            if not daysApplied:
                daysApplied = 0

            if not whichHalfOfDay:
                whichHalfOfDay = 0

            if not isReturnSameDay:
                isReturnSameDay = "False"

            if (
                BasedOnPlanner == False
                and isReturnSameDay == "False"
                and daysApplied == 0
            ):
                if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
                    return JsonResponse(
                        {"error": "Days applied can't be empty"}, safe=False
                    )
                else:
                    messages.error(request, "Days applied can't be empty")
                    return redirect("Applications")

            response = self.make_soap_request(
                soap_headers,
                "FnLeaveApplication",
                applicationNo,
                employeeNo,
                usersId,
                leaveType,
                BasedOnPlanner,
                plannerStartDate,
                float(daysApplied),
                eval(isReturnSameDay),
                int(whichHalfOfDay),
                myAction,
            )
            if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
                if response != "0" and response != None and response != "":
                    return JsonResponse({"response": str(response)}, safe=False)
                return JsonResponse({"error": str(response)}, safe=False)
            else:
                if response != "0" and response != None and response != "":
                    messages.success(request, "Success")
                    return redirect("LeaveDetails", pk=response)
                else:
                    messages.error(request, f"{response}")
                    return redirect("Applications")
        except Exception as e:
            logging.exception(e)
            if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
                return JsonResponse({"error": str(e)}, safe=False)
            else:
                messages.error(request, f"{e}")
                return redirect("Applications")


class NumberOfDaysFilter(UserObjectMixins, View):
    async def get(self, request):
        try:
            planner_date = request.GET.get("planner_date")
            number_of_days = 0
            employeeNo = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )
            async with aiohttp.ClientSession() as session:
                task = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeavePlanLines", "EmployeeNo", "eq", employeeNo
                    )
                )

                response = await asyncio.gather(task)

                for day in response[0]:
                    if day["StartDate"] == planner_date:
                        number_of_days = day["Days"]
                return JsonResponse(number_of_days, safe=False)

        except Exception as e:
            logging.exception(e)
            return JsonResponse({"error": str(e)}, safe=False)


class FnLeaveReliever(UserObjectMixins, View):
    async def get(self, request, pk):
        try:
            async with aiohttp.ClientSession() as session:
                task4 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveRelievers", "LeaveCode", "eq", pk
                    )
                )

                response = await asyncio.gather(task4)

                Relievers = [x for x in response[0]]
                return JsonResponse(Relievers, safe=False)

        except Exception as e:
            logging.exception(e)
            return JsonResponse({"error": str(e)}, safe=False)

    async def post(self, request, pk):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            Reliever = request.POST.get("Reliever")
            myAction = request.POST.get("myAction")

            if Reliever == "" or Reliever == None or Reliever == "0":
                return JsonResponse(
                    {"error": "Reliever field can't be empty"}, safe=False
                )
            else:
                response = self.make_soap_request(
                    soap_headers, "FnLeaveReliever", pk, Reliever, myAction
                )
                print(response)
                if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
                    if response != "0" and response != None and response != "":
                        return JsonResponse({"response": str(response)}, safe=False)
                    return JsonResponse({"error": str(response)}, safe=False)
                else:
                    if response != "0" and response != None and response != "":
                        messages.success(request, "Success")
                        return redirect("LeaveDetails", pk=pk)
                messages.error(request, f"{response}")
                return redirect("LeaveDetails", pk=pk)
        except Exception as e:
            logging.exception(e)
            if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
                return JsonResponse({"error": str(e)}, safe=False)
            else:
                messages.error(request, f"{response}")
                return redirect("LeaveDetails", pk=pk)


class LeaveBalance(UserObjectMixins, View):
    async def get(self, request):
        try:
            leave_type = request.GET.get("leave_type")

            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            Employee_No_ = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )
            response = self.make_soap_request(
                soap_headers,
                "FnGetLeaveBalance",
                Employee_No_,
                leave_type,
            )
            return JsonResponse(response, safe=False)
        except Exception as e:
            logging.exception(e)
            return JsonResponse(str(e), safe=False)


class Applications(UserObjectMixins, View):
    async def get(self, request):
        try:
            UserId = await sync_to_async(request.session.__getitem__)("User_ID")
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            employeeNo = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )
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
                task_approvals_count = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", UserId
                    )
                )
                task1 = asyncio.ensure_future(
                    self.simple_fetch_data(session, "/QyLeaveTypes")
                )
                task_planner = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeavePlanLines", "EmployeeNo", "eq", employeeNo
                    )
                )
                task_planner_header = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session,
                        "/QyLeavePlannerHeaders",
                        "Employee_No_",
                        "eq",
                        employeeNo,
                    )
                )
                response = await asyncio.gather(
                    task_get_leave,
                    task_approvals_count,
                    task1,
                    task_planner,
                    task_planner_header,
                )

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
                LeaveTypes = [x for x in response[2]]
                Plan_Header = [x for x in response[4] if x["Submitted"] == True]
                No_Values = [x["No_"] for x in Plan_Header]

                Plan = [x for x in response[3] if x["DocumentNo"] in No_Values]
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
            "leaveTypes": LeaveTypes,
            "plan": Plan,
        }
        return render(request, "Leave/applications.html", ctx)


class LeaveDetails(UserObjectMixins, View):
    async def get(self, request, pk):
        try:
            ctx = {}
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            Department = await sync_to_async(request.session.__getitem__)("Department")
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            employeeNo = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            open_leave_applications = ""
            if open_leave_count > 0:
                open_leave_applications = await sync_to_async(
                    request.session.__getitem__
                )("open_leave_applications")
            res = {}
            comment = {}

            if "&" in Department:
                Department = Department.replace("&", "%26")

            async with aiohttp.ClientSession() as session:
                task_get_leave = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveApplications", "Application_No", "eq", pk
                    )
                )
                task2 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyDocumentAttachments", "No", "eq", pk
                    )
                )
                task3 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "DocumentNo", "eq", pk
                    )
                )

                task4 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveRelievers", "LeaveCode", "eq", pk
                    )
                )
                task_get_relievers = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session,
                        "/QyEmployees",
                        "Global_Dimension_2_Code",
                        "eq",
                        Department,
                    )
                )
                task1 = asyncio.ensure_future(
                    self.simple_fetch_data(session, "/QyLeaveTypes")
                )

                task_planner = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeavePlanLines", "EmployeeNo", "eq", employeeNo
                    )
                )

                task_comments = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalComments", "DocumentNo", "eq", pk
                    )
                )

                task_planner_header = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session,
                        "/QyLeavePlannerHeaders",
                        "Employee_No_",
                        "eq",
                        employeeNo,
                    )
                )

                response = await asyncio.gather(
                    task_get_leave,
                    task2,
                    task3,
                    task4,
                    task_get_relievers,
                    task1,
                    task_planner,
                    task_comments,
                    task_planner_header,
                )

                for leave in response[0]:
                    res = leave
                allFiles = [x for x in response[1]]
                Approvers = [x for x in response[2]]
                Relievers = [x for x in response[3]]
                relievers = [x for x in response[4] if x["No_"] != employeeNo]
                LeaveTypes = [x for x in response[5]]
                for comment in response[7]:
                    comment = comment
                Plan_Header = [x for x in response[8] if x["Submitted"] == True]
                No_Values = [x["No_"] for x in Plan_Header]

                Plan = [x for x in response[6] if x["DocumentNo"] in No_Values]
                ctx = {
                    "res": res,
                    "username": full_name,
                    "file": allFiles,
                    "Approvers": Approvers,
                    "Relievers": Relievers,
                    "Reliever": relievers,
                    "leave": LeaveTypes,
                    "plan": Plan,
                    "comment": comment,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                    "Employee": Employee,
                }
        except Exception as e:
            messages.error(request, f"{e}")
            return redirect("Applications")
        return render(request, "Leave/leave_details.html", ctx)

    async def post(self, request, pk):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            attachments = request.FILES.getlist("attachment")
            tableID = 50520
            attachment_names = []
            response = False
            for file in attachments:
                fileName = file.name
                attachment_names.append(fileName)
                attachment = base64.b64encode(file.read())
                response = self.upload_attachment(
                    soap_headers,
                    pk,
                    fileName,
                    attachment,
                    tableID,
                )
            if response is not None:
                if response == True:
                    messages.success(
                        request,
                        "Uploaded {} attachments successfully".format(len(attachments)),
                    )
                    return redirect("LeaveDetails", pk=pk)
                messages.error(request, "Upload failed: {}".format(response))
                return redirect("LeaveDetails", pk=pk)
            messages.error(request, "Upload failed: Response from server was None")
            return redirect("LeaveDetails", pk=pk)
        except Exception as e:
            messages.error(request, "Upload failed: {}".format(e))
            logging.exception(e)
            return redirect("LeaveDetails", pk=pk)


class LeaveApproval(UserObjectMixins, View):
    def post(self, request, pk):
        try:
            soap_headers = request.session["soap_headers"]
            employeeNo = request.session["Employee_No_"]

            response = self.make_soap_request(
                soap_headers, "FnRequestLeaveApproval", employeeNo, pk
            )
            if response == True:
                messages.success(request, "Approval request sent successfully")
                return redirect("LeaveDetails", pk=pk)
            messages.error(request, f"{response}")
            return redirect("LeaveDetails", pk=pk)
        except Exception as e:
            messages.error(request, f"{e}")
            print(e)
            return redirect("LeaveDetails", pk=pk)


class LeaveCancelApproval(UserObjectMixins, View):
    def post(self, request, pk):
        try:
            employeeNo = request.session["Employee_No_"]
            soap_headers = request.session["soap_headers"]

            response = self.make_soap_request(
                soap_headers, "FnCancelLeaveApproval", employeeNo, pk
            )
            if response == True:
                messages.success(request, "Approval request cancelled successfully")
                return redirect("LeaveDetails", pk=pk)
            messages.error(request, f"{response}")
            return redirect("LeaveDetails", pk=pk)
        except Exception as e:
            messages.error(request, f"{e}")
            return redirect("LeaveDetails", pk=pk)


class DeleteLeaveAttachment(UserObjectMixins, View):
    def post(self, request, pk):
        try:
            soap_headers = request.session["soap_headers"]
            docID = int(request.POST.get("docID"))
            tableID = int(request.POST.get("tableID"))
            response = self.delete_attachment(soap_headers, pk, docID, tableID)
            if response == True:
                messages.success(request, "Deleted Successfully")
                return redirect("LeaveDetails", pk=pk)
            messages.error(request, response)
            return redirect("LeaveDetails", pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect("LeaveDetails", pk=pk)


class FnGenerateLeaveReport(UserObjectMixins, View):
    def post(self, request, pk):
        try:
            employeeNo = request.session["Employee_No_"]
            soap_headers = request.session["soap_headers"]
            filenameFromApp = "Leave_Report" + pk + ".pdf"

            response = self.make_soap_request(
                soap_headers, "FnGenerateLeaveReport", employeeNo, filenameFromApp, pk
            )
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/pdf",
            )
            responses["Content-Disposition"] = f"inline;filename={filenameFromApp}"
            return responses
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect("LeaveDetails", pk=pk)


class LeaveReports(UserObjectMixins, View):
    async def get(self, request):
        try:
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            User_ID = await sync_to_async(request.session.__getitem__)("User_ID")
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            open_leave_applications = ""
            if open_leave_count > 0:
                open_leave_applications = await sync_to_async(
                    request.session.__getitem__
                )("open_leave_applications")
            Document_Types = [
                "19",
                "20",
            ]
            ctx = {}
            async with aiohttp.ClientSession() as session:
                task1 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", User_ID
                    )
                )
                task2 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveApplications", "User_ID", "eq", User_ID
                    )
                )
                task3 = asyncio.ensure_future(
                    self.simple_fetch_data(session, "/QyLeaveTypes")
                )
                response = await asyncio.gather(task1, task2, task3)
                open_approvals = [
                    x
                    for x in response[0]
                    if x["Status"] == "Open" and x["DocumentType"] in Document_Types
                ]
                approvedLeave = [x for x in response[1] if x["Status"] == "Released"]
                LeaveTypes = [x for x in response[2]]
                ctx = {
                    "username": full_name,
                    "open_approvals": open_approvals,
                    "approvedLeave": approvedLeave,
                    "leave": LeaveTypes,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                    "Employee": Employee,
                }
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("dashboard")
        return render(request, "Leave/reports.html", ctx)

    async def post(self, request):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            employeeNo = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )

            document_type = int(request.POST.get("document_type"))
            documentID = request.POST.get("documentID")

            today_date = datetime.datetime.now().strftime("%Y-%m-%d")

            if document_type == 1:
                filenameFromApp = f"Leave_Statement_{today_date}.pdf"

                response = self.make_soap_request(
                    soap_headers,
                    "FnGenerateLeaveStatement",
                    employeeNo,
                    filenameFromApp,
                    "",
                )
            elif document_type == 2:
                filenameFromApp = f"Leave_Report_{today_date}.pdf"

                response = self.make_soap_request(
                    soap_headers,
                    "FnGenerateLeaveReport",
                    employeeNo,
                    filenameFromApp,
                    documentID,
                )
            elif document_type == 3:
                sectionCode = await sync_to_async(request.session.__getitem__)(
                    "sectionCode"
                )
                departmentCode = await sync_to_async(request.session.__getitem__)(
                    "Department"
                )
                supervisorEmployeeNo = await sync_to_async(request.session.__getitem__)(
                    "Supervisor"
                )
                supervisorTitle = await sync_to_async(request.session.__getitem__)(
                    "Supervisor_Title"
                )
                filenameFromApp = f"Leave_Summary_Report_{today_date}.pdf"

                payload = {
                    "employeeNo": employeeNo,
                    "filenameFromApp": filenameFromApp,
                    "sectionCode": sectionCode,
                    "departmentCode": departmentCode,
                    "supervisorEmployeeNo": supervisorEmployeeNo,
                    "supervisorTitle": supervisorTitle,
                }

                print(payload)

                response = self.make_soap_request(
                    soap_headers,
                    "FnGenerateLeaveSummaryReport",
                    employeeNo,
                    filenameFromApp,
                    sectionCode,
                    departmentCode,
                    supervisorEmployeeNo,
                    supervisorTitle,
                )
            print(response)

            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            buffer.seek(0)

            pdf_data = buffer.getvalue()

            response = HttpResponse(pdf_data, content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="{filenameFromApp}"'
            )
            return response

        except Exception as e:
            messages.error(request, f"{e}")
            print(e)
            return redirect("LeaveReports")


class LeaveAdjustments(UserObjectMixins, View):
    async def get(self, request):
        try:
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            User_ID = await sync_to_async(request.session.__getitem__)("User_ID")
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            open_leave_applications = ""
            if open_leave_count > 0:
                open_leave_applications = await sync_to_async(
                    request.session.__getitem__
                )("open_leave_applications")
            Document_Types = [
                "19",
                "20",
            ]
            ctx = {}
            async with aiohttp.ClientSession() as session:
                task_approvals_count = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", User_ID
                    )
                )
                response = await asyncio.gather(
                    task_approvals_count,
                )
                open_approvals = [
                    x
                    for x in response[0]
                    if x["Status"] == "Open" and x["DocumentType"] in Document_Types
                ]
                ctx = {
                    "username": full_name,
                    "open_approvals": open_approvals,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                    "Employee": Employee,
                }
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("dashboard")
        return render(request, "Leave/adjustments/adjustments.html", ctx)

    async def post(self, request):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            User_ID = await sync_to_async(request.session.__getitem__)("User_ID")
            adjNo = request.POST.get("adjNo")
            description = request.POST.get("description")
            transType = 2
            myAction = request.POST.get("myAction")

            response = self.make_soap_request(
                soap_headers,
                "FnLeaveAdjustment",
                adjNo,
                description,
                transType,
                User_ID,
                myAction,
            )

            if response != None and response != "" and response != 0:
                messages.success(request, "Success")
                return redirect("AdjustmentDetails", pk=response)
            else:
                messages.error(request, f"{response}")
                return redirect("LeaveAdjustments")
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("LeaveAdjustments")


class MyAdjustments(UserObjectMixins, View):
    async def get(self, request):
        try:
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            User_ID = await sync_to_async(request.session.__getitem__)("User_ID")
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            open_leave_applications = ""
            if open_leave_count > 0:
                open_leave_applications = await sync_to_async(
                    request.session.__getitem__
                )("open_leave_applications")
            Document_Types = [
                "19",
                "20",
            ]
            ctx = {}
            async with aiohttp.ClientSession() as session:
                task_approvals_count = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", User_ID
                    )
                )
                task_get_adjustments = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveAdjustmentHeader", "EnteredBy", "eq", User_ID
                    )
                )
                response = await asyncio.gather(
                    task_approvals_count, task_get_adjustments
                )
                open_approvals = [
                    x
                    for x in response[0]
                    if x["Status"] == "Open" and x["DocumentType"] in Document_Types
                ]
                open = [x for x in response[1] if x["Status"] == "Open"]
                pending = [x for x in response[1] if x["Status"] == "Pending Approval"]
                approved = [x for x in response[1] if x["Status"] == "Released"]
                Rejected = [x for x in response[1] if x["Status"] == "Rejected"]
                ctx = {
                    "username": full_name,
                    "open_approvals": open_approvals,
                    "open": open,
                    "pending": pending,
                    "approved": approved,
                    "Rejected": Rejected,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                    "Employee": Employee,
                }
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("dashboard")
        return render(request, "Leave/adjustments/my_adjustment.html", ctx)


class AdjustmentDetails(UserObjectMixins, View):
    async def get(self, request, pk):
        try:
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            User_ID = await sync_to_async(request.session.__getitem__)("User_ID")
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            open_leave_applications = ""
            if open_leave_count > 0:
                open_leave_applications = await sync_to_async(
                    request.session.__getitem__
                )("open_leave_applications")
            Document_Types = [
                "19",
                "20",
            ]
            ctx = {}
            res = {}
            async with aiohttp.ClientSession() as session:
                task_approvals_count = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", User_ID
                    )
                )
                task_get_adj = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveAdjustmentHeader", "Code", "eq", pk
                    )
                )
                task3 = asyncio.ensure_future(
                    self.simple_fetch_data(session, "/QyLeaveTypes")
                )
                task4 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveAdjustmentLines", "HeaderNo", "eq", pk
                    )
                )
                task5 = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "DocumentNo", "eq", pk
                    )
                )

                response = await asyncio.gather(
                    task_approvals_count, task_get_adj, task3, task4, task5
                )
                open_approvals = [
                    x
                    for x in response[0]
                    if x["Status"] == "Open" and x["DocumentType"] in Document_Types
                ]
                for adj in response[1]:
                    res = adj
                LeaveTypes = [x for x in response[2]]
                lines = [x for x in response[3]]
                Approvers = [x for x in response[4]]
                ctx = {
                    "username": full_name,
                    "open_approvals": open_approvals,
                    "res": res,
                    "leave": LeaveTypes,
                    "lines": lines,
                    "Approvers": Approvers,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                    "Employee": Employee,
                }
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("MyAdjustments")
        return render(request, "Leave/adjustments/adjustment_detail.html", ctx)

    async def post(self, request, pk):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            employeeNo = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )
            lineNo = int(request.POST.get("lineNo"))
            leaveType = request.POST.get("leaveType")
            transType = int(request.POST.get("transType"))
            entitlementAdj = float(request.POST.get("entitlementAdj"))
            myAction = request.POST.get("myAction")

            response = self.make_soap_request(
                soap_headers,
                "FnLeaveAdjustmentLine",
                lineNo,
                pk,
                employeeNo,
                leaveType,
                transType,
                entitlementAdj,
                myAction,
            )
            if response == True:
                messages.success(request, "Success")
                return redirect("AdjustmentDetails", pk=pk)
            else:
                messages.error(request, f"{response}")
                return redirect("AdjustmentDetails", pk=pk)
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("AdjustmentDetails", pk=pk)


class FnRequestLeaveAdjustmentApproval(UserObjectMixins, View):
    async def post(self, request, pk):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            response = self.make_soap_request(
                soap_headers,
                "FnRequestLeaveAdjustmentApproval",
                pk,
            )
            if response == True:
                messages.success(request, "Success")
                return redirect("AdjustmentDetails", pk=pk)
            else:
                messages.error(request, f"{response}")
                return redirect("AdjustmentDetails", pk=pk)
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("AdjustmentDetails", pk=pk)


class FnCancelLeaveAdjustmentApproval(UserObjectMixins, View):
    async def post(self, request, pk):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            response = self.make_soap_request(
                soap_headers,
                "FnCancelLeaveAdjustmentApproval",
                pk,
            )
            if response == True:
                messages.success(request, "Success")
                return redirect("AdjustmentDetails", pk=pk)
            else:
                messages.error(request, f"{response}")
                return redirect("AdjustmentDetails", pk=pk)
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("AdjustmentDetails", pk=pk)


class LeavePlanner(UserObjectMixins, View):
    async def get(self, request):
        try:
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            User_ID = await sync_to_async(request.session.__getitem__)("User_ID")
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            open_leave_applications = ""
            if open_leave_count > 0:
                open_leave_applications = await sync_to_async(
                    request.session.__getitem__
                )("open_leave_applications")
            Document_Types = [
                "19",
                "20",
            ]
            ctx = {}
            async with aiohttp.ClientSession() as session:
                task_approvals_count = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", User_ID
                    )
                )
                response = await asyncio.gather(
                    task_approvals_count,
                )
                open_approvals = [
                    x
                    for x in response[0]
                    if x["Status"] == "Open" and x["DocumentType"] in Document_Types
                ]
                ctx = {
                    "username": full_name,
                    "open_approvals": open_approvals,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                    "Employee": Employee,
                }
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("dashboard")
        return render(request, "Leave/planner/planner.html", ctx)

    async def post(self, request):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            employeeNo = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )
            plannerNo = request.POST.get("plannerNo")
            myAction = request.POST.get("myAction")

            response = self.make_soap_request(
                soap_headers,
                "FnLeavePlannerHeader",
                plannerNo,
                employeeNo,
                myAction,
            )
            if response != "0" and response != None and response != "":
                return JsonResponse({"response": str(response)}, safe=False)
            return JsonResponse({"error": str(response)}, safe=False)
        except Exception as e:
            logging.exception(e)
            return JsonResponse({"error": str(e)}, safe=False)


class FnLeavePlannerLine(UserObjectMixins, View):
    async def get(self, request, pk):
        try:
            employeeNo = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )
            Lines = []
            async with aiohttp.ClientSession() as session:
                task_get_training_lines = asyncio.ensure_future(
                    self.simple_double_filtered_data(
                        session,
                        "/QyLeavePlanLines",
                        "DocumentNo",
                        "eq",
                        pk,
                        "and",
                        "EmployeeNo",
                        "eq",
                        employeeNo,
                    )
                )

                response = await asyncio.gather(task_get_training_lines)

                Lines = [x for x in response[0]]

                return JsonResponse(Lines, safe=False)

        except Exception as e:
            logging.exception(e)
            return JsonResponse({"error": str(e)}, safe=False)

    async def post(self, request, pk):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            lineNo = int(request.POST.get("lineNo"))
            startDate = dates.strptime(request.POST.get("startDate"), "%Y-%m-%d").date()
            endDate = dates.strptime(request.POST.get("endDate"), "%Y-%m-%d").date()
            myAction = request.POST.get("myAction")

            response = self.make_soap_request(
                soap_headers,
                "FnLeavePlannerLine",
                lineNo,
                pk,
                startDate,
                endDate,
                myAction,
            )
            if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
                if response == True:
                    return JsonResponse({"response": "Success"}, safe=False)
                return JsonResponse({"error": str(response)}, safe=False)
            else:
                if response == True:
                    messages.success(request, "Success")
                    return redirect("PlannerDetails", pk=pk)
                else:
                    messages.error(request, f"{response}")
                    return redirect("PlannerDetails", pk=pk)
        except Exception as e:
            logging.exception(e)
            if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
                return JsonResponse({"error": str(e)}, safe=False)
            else:
                messages.error(request, f"{e}")
                return redirect("PlannerDetails", pk=pk)


class FnSubmitLeavePlanner(UserObjectMixins, View):
    def post(self, request, pk):
        try:
            soap_headers = request.session["soap_headers"]
            employeeNo = request.session["Employee_No_"]

            response = self.make_soap_request(
                soap_headers, "FnSubmitLeavePlanner", pk, employeeNo
            )
            if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
                if response == True:
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Approval request sent successfully",
                        }
                    )
            else:
                if response == True:
                    messages.success(request, "Success")
                    return redirect("PlannerDetails", pk=pk)
                else:
                    messages.error(request, f"{response}")
                    return redirect("MyPlans")
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
                return JsonResponse({"success": False, "error": error})
            else:
                messages.error(request, f"{e}")
                return redirect("MyPlans")


class MyPlans(UserObjectMixins, View):
    async def get(self, request):
        try:
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            User_ID = await sync_to_async(request.session.__getitem__)("User_ID")
            employeeNo = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            open_leave_applications = ""
            if open_leave_count > 0:
                open_leave_applications = await sync_to_async(
                    request.session.__getitem__
                )("open_leave_applications")
            Document_Types = [
                "19",
                "20",
            ]
            ctx = {}
            async with aiohttp.ClientSession() as session:
                task_approvals_count = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", User_ID
                    )
                )
                task_get_planners = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session,
                        "/QyLeavePlannerHeaders",
                        "Employee_No_",
                        "eq",
                        employeeNo,
                    )
                )
                response = await asyncio.gather(task_approvals_count, task_get_planners)
                open_approvals = [
                    x
                    for x in response[0]
                    if x["Status"] == "Open" and x["DocumentType"] in Document_Types
                ]
                open_plans = [x for x in response[1] if x["Submitted"] == False]
                submitted = [x for x in response[1] if x["Submitted"] == True]
                ctx = {
                    "username": full_name,
                    "open_approvals": open_approvals,
                    "open_plans": open_plans,
                    "submitted": submitted,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                    "Employee": Employee,
                }
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("dashboard")
        return render(request, "Leave/planner/my_plans.html", ctx)


class PlannerDetails(UserObjectMixins, View):
    async def get(self, request, pk):
        try:
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            User_ID = await sync_to_async(request.session.__getitem__)("User_ID")
            Employee = await sync_to_async(request.session.__getitem__)("Employee")
            open_leave_count = await sync_to_async(request.session.__getitem__)(
                "open_leave_count"
            )
            open_leave_applications = ""
            if open_leave_count > 0:
                open_leave_applications = await sync_to_async(
                    request.session.__getitem__
                )("open_leave_applications")
            Document_Types = [
                "19",
                "20",
            ]
            ctx = {}
            res = {}
            async with aiohttp.ClientSession() as session:
                task_approvals_count = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", User_ID
                    )
                )
                task_get_plan = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeavePlannerHeaders", "No_", "eq", pk
                    )
                )
                task_get_plan_lines = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeavePlanLines", "DocumentNo", "eq", pk
                    )
                )
                response = await asyncio.gather(
                    task_approvals_count, task_get_plan, task_get_plan_lines
                )
                open_approvals = [
                    x
                    for x in response[0]
                    if x["Status"] == "Open" and x["DocumentType"] in Document_Types
                ]
                for plan in response[1]:
                    res = plan
                lines = [x for x in response[2]]
                ctx = {
                    "username": full_name,
                    "open_approvals": open_approvals,
                    "res": res,
                    "lines": lines,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                    "Employee": Employee,
                }
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("dashboard")
        return render(request, "Leave/planner/planner_detail.html", ctx)


class FnReOpenLeavePlanner(UserObjectMixins, View):
    def post(self, request, pk):
        try:
            soap_headers = request.session["soap_headers"]
            employeeNo = request.session["Employee_No_"]
            response = self.make_soap_request(
                soap_headers, "FnReOpenLeavePlanner", pk, employeeNo
            )

            if response == True:
                messages.success(request, "Success")
                return redirect("PlannerDetails", pk=pk)
            else:
                messages.error(request, f"{response}")
                return redirect("PlannerDetails", pk=pk)
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("MyPlans")


class LeaveDashboard(UserObjectMixins, View):
    async def get(self, request):
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
            Document_Types = ["19", "20"]
            ctx = {}

            print(Department)

            if "&" in Department:
                Department = Department.replace("&", "%26")

            async with aiohttp.ClientSession() as session:
                task_approvals_count = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "ApproverID", "eq", User_ID
                    )
                )
                department_employees = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session,
                        "/QyEmployees",
                        "Global_Dimension_2_Code",
                        "eq",
                        Department,
                    )
                )
                get_leave = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyLeaveApplications", "Status", "eq", "Released"
                    )
                )
                response = await asyncio.gather(
                    task_approvals_count, department_employees, get_leave
                )

                open_approvals = [
                    x
                    for x in response[0]
                    if x["Status"] == "Open" and x["DocumentType"] in Document_Types
                ]

                employees = [x for x in response[1]]
                user_ids = [employee["User_ID"] for employee in employees]

                department_leave = [x for x in response[2] if x["User_ID"] in user_ids]

                today = datetime.date.today()

                future_department_leave = [
                    x
                    for x in department_leave
                    if datetime.datetime.strptime(
                        x["Resumption_Date"], "%Y-%m-%d"
                    ).date()
                    > today
                ]

                start_date_passed_leave = [
                    x
                    for x in future_department_leave
                    if datetime.datetime.strptime(x["Start_Date"], "%Y-%m-%d").date()
                    <= today
                ]

                planned_department_leave = [
                    x
                    for x in department_leave
                    if datetime.datetime.strptime(
                        x["Resumption_Date"], "%Y-%m-%d"
                    ).date()
                    > today
                    and x["Use_Planner"] == True
                ]

                un_planned_department_leave = [
                    x
                    for x in department_leave
                    if datetime.datetime.strptime(
                        x["Resumption_Date"], "%Y-%m-%d"
                    ).date()
                    > today
                    and x["Use_Planner"] == False
                ]

                if "%26" in Department:
                    Department = Department.replace("%26", "&")

                ctx = {
                    "username": full_name,
                    "open_approvals": open_approvals,
                    "department_leave": future_department_leave,
                    "employees": employees,
                    "planned_department_leave": planned_department_leave,
                    "start_date_passed_leave": start_date_passed_leave,
                    "Department": Department,
                    "un_planned_department_leave": un_planned_department_leave,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                    "Employee": Employee,
                }
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("dashboard")
        return render(request, "leave_dashboard.html", ctx)


class FnArchiveLeaveApplication(UserObjectMixins, View):
    async def post(self, request, pk):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            response = None

            response = self.make_soap_request(
                soap_headers, "FnArchiveLeaveApplication", pk
            )
            print(response)
            if response == True:
                messages.success(request, "Successfully archived")
                return redirect("Applications")
            else:
                messages.error(request, f"{response}")
                return redirect("Applications")
        except Exception as e:
            messages.error(request, f"{response}")
            return redirect("Applications")


class FnArchiveLeaveApplication(UserObjectMixins, View):
    async def post(self, request, pk):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            response = None

            response = self.make_soap_request(
                soap_headers, "FnArchiveLeaveApplication", pk
            )
            print(response)
            if response == True:
                messages.success(request, "Successfully archived")
                return redirect("Applications")
            else:
                messages.error(request, f"{response}")
                return redirect("Applications")
        except Exception as e:
            messages.error(request, f"{response}")
            return redirect("Applications")
