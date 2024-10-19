import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from myRequest.views import UserObjectMixins
from django.contrib import messages


class Documentation(UserObjectMixins, View):
    def get(self, request):
        full_name = request.session["full_name"]

        Employee = request.session["Employee"]

        ctx = {
            "username": full_name,
            "Employee": Employee,
        }
        return render(request, "documentation.html", ctx)
