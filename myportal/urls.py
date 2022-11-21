from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from globus_portal_framework.urls import register_custom_index
from myportal.views import mysearch, file_detail

register_custom_index('custom_search', ['schema-org-index'])


urlpatterns = [
    # Provides the basic search portal
    path('<custom_search:index>/resource/<filename>', file_detail, name='resource'),
    path('<custom_search:index>/', mysearch, name='search'),

    path('', include('globus_portal_framework.urls')),
    path('', include('social_django.urls', namespace='social')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
