from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from ms_identity_web.django.msal_views_and_urls import MsalViews

msal_urls = MsalViews(settings.MS_IDENTITY_WEB).url_patterns()


urlpatterns = [
    path("selfservice/admin/", admin.site.urls),
    path("selfservice/", include("dashboard.urls")),
    path("selfservice/", include("authentication.urls")),
    path("selfservice/", include("base.urls")),
    path("selfservice/", include("HR.urls")),
    path("selfservice/", include("approvals.urls")),
    path("selfservice/", include("documentation.urls")),
    path(
        f"selfservice/{settings.AAD_CONFIG.django.auth_endpoints.prefix}/",
        include(msal_urls),
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
