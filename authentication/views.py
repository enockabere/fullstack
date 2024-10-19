import asyncio
import json
import random
import string
import aiohttp
from django.shortcuts import render, redirect
from myRequest.views import UserObjectMixins
from django.contrib import messages
from django.views import View
from django.conf import settings as config
from asgiref.sync import sync_to_async
import requests
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.http import JsonResponse


class Login_View(UserObjectMixins,View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        default_password = 'Z0FBQUFBQm5Fa1RnYzhPbS1fM1hIVzNlUzVrcVBaRUFsVC1LS2lzLVNUUFV3MmdBalFweHJqMmp3X2pZdnlETm14ZUp2UGlZdFJvdUNHMUkwMHpJNnZMTzN3ck9WclcyYUE9PQ=='
        decrypted = self.pass_decrypt(default_password)

        if decrypted == password:
            # Respond with different paths based on the condition
            return JsonResponse({'redirect_url': '/selfservice/forgot-password/'})
        else:
            return JsonResponse({'redirect_url': '/selfservice/user-dashboard/'})
        

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Add this if you are not using CSRF tokens correctly
def send_otps(request):
    if request.method == 'POST':
        # Your logic for handling POST requests
        return JsonResponse({'status': 'OTP sent'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)



class Send_Otp(View):
    def post(self, request):
        print("POST request received")  # Log that the POST method is called

        try:
            data = json.loads(request.body)  # Read JSON body
            email = data.get('email')
            print("Email received:", email)  # Log the email received in the request

            if email:
                # Generate OTP logic
                otp = ''.join(random.choices(string.digits, k=6))  # 6-digit OTP
                otp_data = {"otp": otp, "otp_email": email}
                request.session['otp_data'] = otp_data  # Store OTP in session
                print("OTP generated and stored:", otp_data)  # Log the OTP generation and storage
                
                return JsonResponse({'message': 'OTP sent to email', 'status': 'success'})
            else:
                print("Email missing in the request")  # Log missing email case
                return JsonResponse({'message': 'Email is required', 'status': 'error'}, status=400)
        except json.JSONDecodeError as e:
            print("Error parsing JSON:", e)  # Log JSON parsing errors
            return JsonResponse({'message': 'Invalid data', 'status': 'error'}, status=400)

    def get(self, request):
        print("GET request received")  # Log if a GET request is mistakenly used
        return JsonResponse({'message': 'Method not allowed'}, status=405)
        
class Resend_Otp(UserObjectMixins,View):
    def post(self, request):
        email = request.session['otp_data']['otp_email']
        if email:            
            return JsonResponse({'message': 'OTP sent to email', 'status': 'success'})
        else:
            return JsonResponse({'message': 'Email is required', 'status': 'error'}, status=400)
  


class azure_ad_callback(UserObjectMixins, View):
    def get(self, request):
        try:
            code = request.GET.get("code")

            if code:
                token_url = f"https://login.microsoftonline.com/{config.AZURE_AD_TENANT_ID}/oauth2/v2.0/token"
                token_data = {
                    "grant_type": "authorization_code",
                    "code": code,
                    "scope": "https://graph.microsoft.com/.default",
                    "client_id": config.AZURE_AD_CLIENT_ID,
                    "client_secret": config.AZURE_AD_CLIENT_SECRET,
                    "redirect_uri": config.AZURE_AD_REDIRECT_URI,
                }

                token_response = requests.post(token_url, data=token_data)

                if token_response.status_code == 200:
                    token = token_response.json()
                    access_token = token.get("access_token")
                    graph_api_url = "https://graph.microsoft.com/v1.0/me"
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                    }

                    response = requests.get(url=graph_api_url, headers=headers)

                    if response.status_code == 200:
                        user_data = response.json()

                        user_name = user_data.get("displayName")
                        user_email = user_data.get("userPrincipalName").lower()

                        users = self.one_filter(
                            "/QyUserSetup", "EMail", "eq", user_email
                        )
                        if users[0] == 0:
                            error_message = (
                                f"{user_email} does not exist in the user setup"
                            )
                            raise Exception(error_message)
                        else:
                            for user in users[1]:
                                missing_keys = [
                                    key
                                    for key in [
                                        "UserID",
                                        "HODUser",
                                    ]
                                    if key not in user
                                    or (user.get(key) is None or user.get(key) == "")
                                ]
                                if missing_keys:
                                    error_message = (
                                        f"Missing data for: {', '.join(missing_keys)}"
                                    )
                                    raise ValueError(error_message)
                                if (
                                    user["CustomerNo"] == None
                                    or user["CustomerNo"] == ""
                                ):
                                    request.session["Customer_No_"] = "None"
                                else:
                                    request.session["Customer_No_"] = user["CustomerNo"]
                                request.session["User_ID"] = user["UserID"]
                                if user["EMail"] == None or user["EMail"] == "":
                                    request.session["E_Mail"] = "None"
                                else:
                                    request.session["E_Mail"] = user["EMail"]
                                if user["PhoneNo"] == None or user["PhoneNo"] == "":
                                    request.session["PhoneNo"] = "None"
                                else:
                                    request.session["PhoneNo"] = user["PhoneNo"]
                                request.session["HOD_User"] = user["HODUser"]

                                soap_headers = {
                                    "username": config.WEB_SERVICE_UID,
                                    "password": config.WEB_SERVICE_PWD,
                                }
                                request.session["soap_headers"] = soap_headers

                                if (
                                    user["EmployeeNo"] == None
                                    or user["EmployeeNo"] == ""
                                ):
                                    request.session["full_name"] = user["UserID"]
                                    request.session["open_leave_count"] = 0
                                    request.session["open_leave_applications"] = 0
                                    request.session["Department"] = "None"
                                    request.session["Employee"] = False
                                    messages.success(
                                        request,
                                        f"Success. Logged in as {request.session['User_ID']}",
                                    )
                                    return redirect("Approval")
                                else:
                                    request.session["Employee_No_"] = user["EmployeeNo"]
                                    request.session["Employee"] = True

                                Employee_No_ = request.session["Employee_No_"]
                                User_ID = request.session["User_ID"]

                                employees = self.one_filter(
                                    "/QyEmployees", "No_", "eq", Employee_No_
                                )

                                if employees[0] == 0:
                                    error_message = f"{Employee_No_} does not exist in the employees setup"
                                    raise Exception(error_message)
                                else:
                                    task_get_leave = self.one_filter(
                                        "/QyLeaveApplications",
                                        "User_ID",
                                        "eq",
                                        User_ID,
                                    )
                                    open_leave_count = len(
                                        [
                                            x
                                            for x in task_get_leave[1]
                                            if x["Status"] == "Open"
                                        ]
                                    )

                                    open_leave_applications = []

                                    if open_leave_count > 0:
                                        open_leave_applications = [
                                            x["Application_No"]
                                            for x in employees[1]
                                            if x["Status"] == "Open"
                                        ]

                                        request.session[
                                            "open_leave_applications"
                                        ] = open_leave_applications
                                    request.session[
                                        "open_leave_count"
                                    ] = open_leave_count
                                    for employee in employees[1]:
                                        missing_keys = [
                                            key
                                            for key in [
                                                "First_Name",
                                            ]
                                            if key not in employee
                                            or (
                                                employee.get(key) is None
                                                or employee.get(key) == ""
                                            )
                                        ]
                                        if missing_keys:
                                            error_message = f"Missing data for: {', '.join(missing_keys)}"
                                            raise ValueError(error_message)
                                        request.session["First_Name"] = employee.get(
                                            "First_Name", "None"
                                        )

                                        # Set Middle_Name
                                        middle_name = employee.get("Middle_Name", "")
                                        if middle_name == "":
                                            middle_name = "None"
                                        request.session["Middle_Name"] = middle_name

                                        # Set Last_Name
                                        last_name = employee.get("Last_Name", "")
                                        if last_name == "":
                                            last_name = "None"
                                        request.session["Last_Name"] = last_name

                                        # Create full_name
                                        full_name = employee["First_Name"]
                                        if middle_name != "None":
                                            full_name += " " + middle_name
                                        if last_name != "None":
                                            full_name += " " + last_name
                                        request.session["full_name"] = full_name

                                        if (
                                            employee["Global_Dimension_1_Code"] == None
                                            or employee["Global_Dimension_1_Code"] == ""
                                        ):
                                            request.session["sectionCode"] = "None"
                                        else:
                                            request.session["sectionCode"] = employee[
                                                "Global_Dimension_1_Code"
                                            ]

                                        if (
                                            employee["Global_Dimension_2_Code"] == None
                                            or employee["Global_Dimension_2_Code"] == ""
                                        ):
                                            request.session["Department"] = "None"
                                        else:
                                            request.session["Department"] = employee[
                                                "Global_Dimension_2_Code"
                                            ]

                                        if (
                                            employee["Supervisor_Title"] == None
                                            or employee["Supervisor_Title"] == ""
                                        ):
                                            request.session["Supervisor_Title"] = "None"

                                        else:
                                            request.session[
                                                "Supervisor_Title"
                                            ] = employee["Supervisor_Title"]

                                        if (
                                            employee["Supervisor"] == None
                                            or employee["Supervisor"] == ""
                                        ):
                                            request.session["Supervisor"] = "None"

                                        else:
                                            request.session["Supervisor"] = employee[
                                                "Supervisor"
                                            ]

                                        if (
                                            employee["Job_Position"] == None
                                            or employee["Job_Position"] == ""
                                        ):
                                            request.session[
                                                "Job_Position"
                                            ] = "Job Position"
                                        else:
                                            request.session["Job_Position"] = employee[
                                                "Job_Position"
                                            ]

                                        if (
                                            employee["Job_Title"] == None
                                            or employee["Job_Title"] == ""
                                        ):
                                            request.session["Job_Title"] = "Job Title"
                                        else:
                                            request.session["Job_Title"] = employee[
                                                "Job_Title"
                                            ]
                                        messages.success(
                                            request,
                                            f"Success. Logged in as {request.session['full_name']}",
                                        )
                                        saved_url = request.session.get("saved_url")
                                        if saved_url is not None:
                                            if "saved_url" in request.session:
                                                del request.session["saved_url"]

                                            return HttpResponseRedirect(saved_url)
                                        else:
                                            return redirect("dashboard")
                                    error_message = f"{Employee_No_} does not exist in the employees setup"
                                    raise Exception(error_message)

                            error_message = (
                                f"{user_email} does not exist in the user setup"
                            )
                            raise Exception(error_message)

                    else:
                        error_message = f"Graph API Error: {response.text}"
                        raise Exception(error_message)

                else:
                    error_message = f"Token Exchange Error: {token_response.text}"
                    raise Exception(error_message)
        except Exception as e:
            print(e)
            messages.error(request, f"{e}")
            return redirect("Login")


class Login(UserObjectMixins, View):
    async def get(self, request):
        return render(request, "index.html")

    async def post(self, request):
        try:
            username = request.POST.get("username").upper().strip()
            password = request.POST.get("password")

            if not username or not password:
                if not username:
                    error_message = "Username cannot be empty"
                else:
                    error_message = "Password cannot be empty"
                raise ValueError(error_message)

            async with aiohttp.ClientSession() as session:
                task_get_user_setup = asyncio.ensure_future(
                    self.fetch_data(
                        session, username, password, "/QyUserSetup", "UserID", "eq"
                    )
                )
                user_response = await asyncio.gather(task_get_user_setup)
                if user_response[0]["status_code"] == 200:
                    for data in user_response[0]["data"]:
                        missing_keys = [
                            key
                            for key in [
                                "UserID",
                                "HODUser",
                            ]
                            if key not in data
                            or (data.get(key) is None or data.get(key) == "")
                        ]
                        if missing_keys:
                            error_message = (
                                f"Missing data for: {', '.join(missing_keys)}"
                            )
                            raise ValueError(error_message)

                        if data["CustomerNo"] == None or data["CustomerNo"] == "":
                            await sync_to_async(request.session.__setitem__)(
                                "Customer_No_", "None"
                            )
                        else:
                            await sync_to_async(request.session.__setitem__)(
                                "Customer_No_", data["CustomerNo"]
                            )
                        await sync_to_async(request.session.__setitem__)(
                            "User_ID", data["UserID"]
                        )
                        if data["EMail"] == None or data["EMail"] == "":
                            await sync_to_async(request.session.__setitem__)(
                                "E_Mail", "None"
                            )
                        else:
                            await sync_to_async(request.session.__setitem__)(
                                "E_Mail", data["EMail"]
                            )
                        if data["PhoneNo"] == None or data["PhoneNo"] == "":
                            await sync_to_async(request.session.__setitem__)(
                                "PhoneNo", "None"
                            )
                        else:
                            await sync_to_async(request.session.__setitem__)(
                                "PhoneNo", data["PhoneNo"]
                            )
                        await sync_to_async(request.session.__setitem__)(
                            "HOD_User", data["HODUser"]
                        )
                        soap_headers = {
                            "username": config.WEB_SERVICE_UID,
                            "password": config.WEB_SERVICE_PWD,
                        }
                        await sync_to_async(request.session.__setitem__)(
                            "soap_headers", soap_headers
                        )

                        if data["EmployeeNo"] == None or data["EmployeeNo"] == "":
                            await sync_to_async(request.session.__setitem__)(
                                "full_name",
                                data["UserID"],
                            )
                            await sync_to_async(request.session.__setitem__)(
                                "open_leave_count", 0
                            )
                            await sync_to_async(request.session.__setitem__)(
                                "open_leave_applications", 0
                            )
                            await sync_to_async(request.session.__setitem__)(
                                "Department", "None"
                            )
                            await sync_to_async(request.session.__setitem__)(
                                "Employee", False
                            )
                            messages.success(
                                request,
                                f"Success. Logged in as {request.session['User_ID']}",
                            )
                            return redirect("Approval")

                        else:
                            await sync_to_async(request.session.__setitem__)(
                                "Employee_No_", data["EmployeeNo"]
                            )
                            await sync_to_async(request.session.__setitem__)(
                                "Employee", True
                            )

                        await sync_to_async(request.session.save)()

                        Employee_No_ = await sync_to_async(request.session.__getitem__)(
                            "Employee_No_"
                        )

                        User_ID = await sync_to_async(request.session.__getitem__)(
                            "User_ID"
                        )

                        get_task_employee = asyncio.ensure_future(
                            self.fetch_one_filtered_data(
                                session, "/QyEmployees", "No_", "eq", Employee_No_
                            )
                        )

                        task_get_leave = asyncio.ensure_future(
                            self.simple_one_filtered_data(
                                session,
                                "/QyLeaveApplications",
                                "User_ID",
                                "eq",
                                User_ID,
                            )
                        )

                        employee_response = await asyncio.gather(
                            get_task_employee, task_get_leave
                        )

                        open_leave_count = len(
                            [x for x in employee_response[1] if x["Status"] == "Open"]
                        )

                        open_leave_applications = []

                        if open_leave_count > 0:
                            open_leave_applications = [
                                x["Application_No"]
                                for x in employee_response[1]
                                if x["Status"] == "Open"
                            ]

                            await sync_to_async(request.session.__setitem__)(
                                "open_leave_applications", open_leave_applications
                            )

                        await sync_to_async(request.session.__setitem__)(
                            "open_leave_count", open_leave_count
                        )

                        for data in employee_response[0]["data"]:
                            missing_keys = [
                                key
                                for key in [
                                    "First_Name",
                                ]
                                if key not in data
                                or (data.get(key) is None or data.get(key) == "")
                            ]
                            if missing_keys:
                                error_message = (
                                    f"Missing data for: {', '.join(missing_keys)}"
                                )
                                raise ValueError(error_message)
                            await sync_to_async(request.session.__setitem__)(
                                "First_Name", data.get("First_Name", "None")
                            )

                            # Set Middle_Name
                            middle_name = data.get("Middle_Name", "")
                            if middle_name == "":
                                middle_name = "None"
                            await sync_to_async(request.session.__setitem__)(
                                "Middle_Name", middle_name
                            )

                            last_name = data.get("Last_Name", "")
                            if last_name == "":
                                last_name = "None"
                            await sync_to_async(request.session.__setitem__)(
                                "Last_Name", last_name
                            )

                            full_name = data["First_Name"]
                            if middle_name != "None":
                                full_name += " " + middle_name
                            if last_name != "None":
                                full_name += " " + last_name
                            await sync_to_async(request.session.__setitem__)(
                                "full_name", full_name
                            )

                            if (
                                data["Global_Dimension_1_Code"] == None
                                or data["Global_Dimension_1_Code"] == ""
                            ):
                                await sync_to_async(request.session.__setitem__)(
                                    "sectionCode", "None"
                                )
                            else:
                                await sync_to_async(request.session.__setitem__)(
                                    "sectionCode", data["Global_Dimension_1_Code"]
                                )

                            if (
                                data["Global_Dimension_2_Code"] == None
                                or data["Global_Dimension_2_Code"] == ""
                            ):
                                await sync_to_async(request.session.__setitem__)(
                                    "Department", "None"
                                )
                            else:
                                await sync_to_async(request.session.__setitem__)(
                                    "Department", data["Global_Dimension_2_Code"]
                                )

                            if (
                                data["Supervisor_Title"] == None
                                or data["Supervisor_Title"] == ""
                            ):
                                await sync_to_async(request.session.__setitem__)(
                                    "Supervisor_Title", "None"
                                )
                            else:
                                await sync_to_async(request.session.__setitem__)(
                                    "Supervisor_Title", data["Supervisor_Title"]
                                )

                            if data["Supervisor"] == None or data["Supervisor"] == "":
                                await sync_to_async(request.session.__setitem__)(
                                    "Supervisor", "None"
                                )
                            else:
                                await sync_to_async(request.session.__setitem__)(
                                    "Supervisor", data["Supervisor"]
                                )

                            if (
                                data["Job_Position"] == None
                                or data["Job_Position"] == ""
                            ):
                                request.session["Job_Position"] = "Job Position"
                            else:
                                request.session["Job_Position"] = data["Job_Position"]

                            if data["Job_Title"] == None or data["Job_Title"] == "":
                                request.session["Job_Title"] = "Job Title"
                            else:
                                request.session["Job_Title"] = data["Job_Title"]
                            messages.success(
                                request,
                                f"Success. Logged in as {request.session['full_name']}",
                            )
                            saved_url = request.session.get("saved_url")
                            if saved_url is not None:
                                if "saved_url" in request.session:
                                    del request.session["saved_url"]

                                return HttpResponseRedirect(saved_url)
                            else:
                                return redirect("dashboard")
                        messages.error(request, "Employee number not recognized")
                        return redirect("Login")
                    messages.error(request, "User ID not recognized")
                    return redirect("Login")
                messages.error(request, "Authentication Error: Invalid credentials")
                return redirect("Login")
        except ValueError as e:
            print(e)
            messages.error(request, str(e))
            return redirect("Login")
        except Exception as e:
            print(e)
            messages.error(request, f"{e}")
            return redirect("Login")


def logout(request):
    try:
        request.session.flush()
        messages.success(request, "Logged out successfully")
        return redirect("Login")
    except KeyError:
        print(False)
    return redirect("Login")
