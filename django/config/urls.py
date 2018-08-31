from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Swagger API')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('user.urls')),
    url(r'^', include('stackoverflow.urls')),
    url(r'^api/v1/', include('api.urls')),
    url(r'^swagger/', schema_view)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)