
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.views.i18n import set_language


urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', set_language, name='set_language'),
    path('', include('membership.urls')),
    path('dp_finance/', include('finance.urls')),
    path('administration/admin/', include('administration.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)


# Point to a custom view function (App_Name.views_file.function_name)
handler404 = 'membership.views.custom_page_404_not_found'
