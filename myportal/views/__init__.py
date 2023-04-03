from django.urls import path, include
from myportal.views import api_account, api_resource
from myportal.views.views import temp_view, file_detail, mysearch, GetAccountProfile
from globus_portal_framework.urls import register_custom_index

register_custom_index('custom_search', ['schema-org-index'])

urlpatterns = [
    # Provides the basic search portal
    path('<custom_search:index>/resource/<uuid>', file_detail, name='resource'),
    path('<custom_search:index>/', mysearch, name='search'),

    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', GetAccountProfile.as_view(), name='account-profile'),
    path('callback/', temp_view, name='temp-view'),

    path('api/resource/get/<uuid>', api_resource.GetResourceSchemaorg.as_view(), name='api-resource-get'),
    path('api/resource/list/', api_resource.GetResourceSchemaorgList.as_view(), name='api-resource-list'),
    path('api/resource/publish/', api_resource.PublishResource.as_view(), name='api-resource-publish'),
    path('api/resource/status/', api_resource.GetResourceStatus.as_view(), name='api-resource-status'),
    path('api/resource/update/', api_resource.UpdateResource.as_view(), name='api-resource-update'), # update resource info
    path('api/accounts/token/verify/', api_account.VerifyToken.as_view(), name='token-verify'),
    path('api/accounts/token/code/', api_account.GetCode.as_view(), name='get-code'),
    path('api/accounts/token/get/', api_account.GetToken.as_view(), name='token-get'),
    path('api/accounts/token/refresh/', api_account.GetToken.as_view(), name='token-refresh'),
    path('api/accounts/profile/', api_account.VerifyToken.as_view(), name='user-profile'),

]
