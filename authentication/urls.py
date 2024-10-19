from django.urls import path, re_path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path("", views.Login.as_view(), name="Login"),
    path("logout/", views.logout, name="logout"),
    path("auth/redirect", views.azure_ad_callback.as_view(), name="azure_ad_callback"),
    path("login_view/", views.Login_View.as_view(), name="login_view"),
    re_path(r"^(?!api/).*$", TemplateView.as_view(template_name="index.html")),
    path('send-otp/', views.Send_Otp.as_view(), name='send_otp'),
    path('resend-otp/',views.Resend_Otp.as_view(), name='resend_otp'),
    path('send-otps/', views.send_otps, name='send_otps'),
]
