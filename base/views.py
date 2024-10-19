import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from myRequest.views import UserObjectMixins
from django.contrib import messages
import aiohttp
import asyncio
from asgiref.sync import sync_to_async
import io as BytesIO
import base64
from django.http import HttpResponse


class Profile(UserObjectMixins, View):
    async def get(self, request):
        try:
            ctx = {}
            User_ID = await sync_to_async(request.session.__getitem__)("User_ID")
            full_name = await sync_to_async(request.session.__getitem__)("full_name")
            Department = await sync_to_async(request.session.__getitem__)("Department")
            First_Name = await sync_to_async(request.session.__getitem__)("First_Name")
            Middle_Name = await sync_to_async(request.session.__getitem__)(
                "Middle_Name"
            )
            Last_Name = await sync_to_async(request.session.__getitem__)("Last_Name")
            E_Mail = await sync_to_async(request.session.__getitem__)("E_Mail")
            PhoneNo = await sync_to_async(request.session.__getitem__)("PhoneNo")
            Employee_No_ = await sync_to_async(request.session.__getitem__)(
                "Employee_No_"
            )
            Job_Title = await sync_to_async(request.session.__getitem__)("Job_Title")
            Job_Position = await sync_to_async(request.session.__getitem__)(
                "Job_Position"
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

                ctx = {
                    "open_approvals": open_approvals,
                    "username": full_name,
                    "First_Name": First_Name,
                    "Middle_Name": Middle_Name,
                    "Department": Department,
                    "Last_Name": Last_Name,
                    "E_Mail": E_Mail,
                    "PhoneNo": PhoneNo,
                    "User_ID": User_ID,
                    "Employee_No_": Employee_No_,
                    "Job_Title": Job_Title,
                    "Job_Position": Job_Position,
                    "open_leave_count": open_leave_count,
                    "open_leave_applications": open_leave_applications,
                }
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect("dashboard")
        return render(request, "profile.html", ctx)


class Attachments(UserObjectMixins, View):
    async def get(self, request, pk):
        try:
            Attachments = []
            async with aiohttp.ClientSession() as session:
                task_get_attachments = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyDocumentAttachments", "No", "eq", pk
                    )
                )
                response = await asyncio.gather(task_get_attachments)

                Attachments = [x for x in response[0]]
                return JsonResponse(Attachments, safe=False)

        except Exception as e:
            logging.exception(e)
            return JsonResponse({"error": str(e)}, safe=False)

    async def post(self, request, pk):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)(
                "soap_headers"
            )
            attachments = request.FILES.getlist("attachment")
            tableID = int(request.POST.get("tableID"))
            attachment_names = []
            response = False
            for file in attachments:
                fileName = file.name
                attachment_names.append(fileName)
                attachment = base64.b64encode(file.read())
                response = self.upload_attachment(
                    soap_headers, pk, fileName, attachment, tableID
                )
            if response is not None:
                if response == True:
                    message = "Uploaded {} attachments successfully".format(
                        len(attachments)
                    )
                    return JsonResponse({"success": True, "message": message})
                error = "Upload failed: {}".format(response)
                return JsonResponse({"success": False, "error": error})
            error = "Upload failed: Response from server was None"
            return JsonResponse({"success": False, "error": error})
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({"success": False, "error": error})


class ApprovalRequest(UserObjectMixins, View):
    def post(self, request):
        try:
            soap_headers = request.session["soap_headers"]
            employeeNo = request.session["Employee_No_"]
            headerCode = request.POST.get("headerCode")
            service_name = request.POST.get("service_name")

            response = self.make_soap_request(
                soap_headers, service_name, employeeNo, headerCode
            )
            if response == True:
                return JsonResponse(
                    {"success": True, "message": "Approval request sent successfully"}
                )
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({"success": False, "error": error})


class CancelApprovalForm(UserObjectMixins, View):
    def post(self, request):
        try:
            soap_headers = request.session["soap_headers"]
            employeeNo = request.session["Employee_No_"]
            headerID = request.POST.get("headerID")
            service_name = request.POST.get("service_name")

            response = self.make_soap_request(
                soap_headers, service_name, employeeNo, headerID
            )
            if response == True:
                return JsonResponse(
                    {"success": True, "message": "Cancel Request Successful"}
                )
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({"success": False, "error": error})


class filter_list(UserObjectMixins, View):
    async def get(self, request, pk):
        try:
            query = request.GET.get("query")
            user_id = await sync_to_async(request.session.__getitem__)("User_ID")
            empNo = await sync_to_async(request.session.__getitem__)("Employee_No_")
            filter_one = request.GET.get("filter_one")
            filter_two = request.GET.get("filter_two")
            filter_two_type = request.GET.get("filter_two_type")

            if filter_two_type == "user":
                filter_three = user_id
            elif filter_two_type == "emp":
                filter_three = empNo

            async with aiohttp.ClientSession() as session:
                task = asyncio.ensure_future(
                    self.simple_double_filtered_data(
                        session,
                        query,
                        filter_one,
                        "eq",
                        pk,
                        "and",
                        filter_two,
                        "eq",
                        filter_three,
                    )
                )
                response = await asyncio.gather(task)
                for response in response[0]:
                    data = response
                    return JsonResponse({"success": True, "data": data}, safe=False)
                return JsonResponse({"success": False, "error": "No Loan"})
        except Exception as e:
            logging.exception(e)
            return JsonResponse({"success": False, "error": e})


class RemoveAttachment(UserObjectMixins, View):
    def post(self, request):
        try:
            soap_headers = request.session["soap_headers"]
            docID = int(request.POST.get("docID"))
            tableID = int(request.POST.get("tableID"))
            headerID = request.POST.get("headerID")

            response = self.delete_attachment(soap_headers, headerID, docID, tableID)
            if response == True:
                return JsonResponse(
                    {"success": True, "message": "Deleted successfully"}
                )
            return JsonResponse({"success": False, "message": f"{response}"})
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({"success": False, "error": error})


class ApproversData(UserObjectMixins, View):
    async def get(self, request, pk):
        try:
            Approvers = []
            async with aiohttp.ClientSession() as session:
                task_get_leave_approvers = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyApprovalEntries", "DocumentNo", "eq", pk
                    )
                )

                response = await asyncio.gather(task_get_leave_approvers)

                Approvers = [x for x in response[0] if x["Status"] == "Open"]
                return JsonResponse(Approvers, safe=False)

        except Exception as e:
            logging.exception(e)
            return JsonResponse({"error": str(e)}, safe=False)


class DownloadDocs(UserObjectMixins, View):
    def post(self, request, pk, id):
        try:
            soap_headers = request.session["soap_headers"]
            attachmentID = int(request.POST.get("attachmentID"))
            File_Name = request.POST.get("File_Name")
            File_Extension = request.POST.get("File_Extension")

            response = self.make_soap_request(
                soap_headers, "FnGetDocumentAttachment", pk, attachmentID, int(id)
            )
            file_name = File_Name.split()
            filenameFromApp = file_name[0] + "." + File_Extension
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/ms-excel",
            )
            responses["Content-Disposition"] = f"inline;filename={filenameFromApp}"
            return responses
        except Exception as e:
            messages.error(request, f"{e}")
            return redirect("dashboard")
        
class LeaveBalances(UserObjectMixins, View):
    async def get(self, request):
        try:
            Employee = await sync_to_async(request.session.__getitem__)("Employee")        
            if (request.session["Employee"] == False):
                supervisor = request.session["User_ID"]
            else:
                supervisor = request.session["Employee_No_"]
            
            balances = []
            async with aiohttp.ClientSession() as session:
                task_get_leave_balances = asyncio.ensure_future(
                    self.simple_one_filtered_data(
                        session, "/QyEmployees", "Supervisor", "eq", supervisor
                    )
                )
                
                response = await asyncio.gather(task_get_leave_balances)

                balances = [x for x in response[0] if x["Status"] == "Active"]

                ctx = {
                    "balances": balances,
                    "Employee": Employee
                }
                
                # return JsonResponse(supervisor, safe=False)

        except Exception as e:
            logging.exception(e)
            return JsonResponse({"error": str(e)}, safe=False)
    
        return render(request, "balances.html", ctx)
