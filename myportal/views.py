import json
import os

import requests
from allauth.socialaccount.models import SocialToken
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.http import HttpResponseBadRequest
from django.views import View
from drf_yasg import openapi
from globus_portal_framework import gsearch
from globus_portal_framework.apps import get_setting
from globus_portal_framework.gsearch import post_search, get_search_query, get_search_filters, get_template, \
    get_subject, get_index
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import SimpleLazyObject

from myportal.utils import verify_cilogon_token

INDEX_NAME = "schema-org-index"
class GetResourceSchemaorgRequest(serializers.Serializer):
    # id = serializers.IntegerField()
    pass


def has_valid_cilogon_token(headers):
    authorization_header = headers.get('Authorization')
    if not authorization_header or not authorization_header.startswith('Bearer '):
        return HttpResponseBadRequest('Invalid Authorization header')
    access_token = authorization_header[len('Bearer '):]
    if verify_cilogon_token(access_token) is None:
        return False
    return True


class GetResourceSchemaorg(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=GetResourceSchemaorgRequest, manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description='Authentication token',
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],)
    def post(self, request, uuid):

        print(f"[GetResourceSchemaorg] user={request.user}")
        if not has_valid_cilogon_token(request.headers):
            return Response(
                data={"status": "Please log in first"},
                status=status.HTTP_200_OK,
            )
        serializer = GetResourceSchemaorgRequest(data=request.data)
        if serializer.is_valid():
            subject = get_subject(INDEX_NAME, uuid, AnonymousUser())
            print(f"[GetResourceSchemaorg] subject={subject}")
            try:
                endpoint = subject['all'][0]
            except KeyError:
                return Response(
                    data={"status": "UUID does not exist"},
                    status=status.HTTP_200_OK,
                )
            schemaorg_json = endpoint['schemaorgJson']
            return Response(
                data={"status": "OK", "schemaorg": schemaorg_json},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetResourceSchemaorgListRequest(serializers.Serializer):
    id_list = serializers.IntegerField()


class GetResourceSchemaorgList(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=GetResourceSchemaorgListRequest)
    def post(self, request):
        serializer = GetResourceSchemaorgRequest(data=request.data)
        if serializer.is_valid():
            subject = get_subject(INDEX_NAME, request.id_list, request.user)  # todo
            print(f"[ListResourceSchemaorg] subject={subject}")
            try:
                endpoint = subject['all'][0]
            except KeyError:
                return Response(
                    data={"status": "UUID does not exist"},
                    status=status.HTTP_200_OK,
                )
            schemaorg_json = endpoint['schemaorgJson']
            return Response(
                data={"status": "OK", "schemaorg_list": [schemaorg_json]},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def mysearch(request, index):
    query = get_search_query(request)
    # print(f'[mysearch]{query}')
    filters = get_search_filters(request)
    print(f"[mysearch] user={AnonymousUser()}")
    print(f"[mysearch] user={request.user}")

    search_result = post_search(index, query, filters, AnonymousUser(),
                                request.GET.get('page', 1))
    print(f'[mysearch]search_result = {search_result}')
    context = {'search': search_result}
    return render(request, get_template(index, 'schema-org-index/components/search-results.html'), context)


def file_detail(request, index, uuid):
    subject = get_subject(index, uuid, AnonymousUser())
    print(f"[file_detail] subject={subject}")

    endpoint = subject['all'][0]

    schemaorg_json = endpoint['schemaorgJson']
    print("***")
    print(f"[file_detail] schemaorg_json={schemaorg_json}")

    detail = {'id': schemaorg_json['@id'],
              # 'subject': subject['subject'],
              'size_bytes': subject['size_bytes'],
              'date_published': schemaorg_json['datePublished'],
              'date_modified': schemaorg_json['dateModified'],
              'keywords': schemaorg_json['keywords'],
              }

    if 'creator' in schemaorg_json and schemaorg_json['creator'] is not None:
        detail['creator'] = schemaorg_json['creator']['@list'][0]['name']
    if 'spatialCoverage' in schemaorg_json:
        if schemaorg_json['spatialCoverage'] is not None:
            if schemaorg_json['spatialCoverage']['@type'] == 'Place':
                detail['spatial_coverage'] = schemaorg_json['spatialCoverage']
                detail['spatial_coverage_values'] = schemaorg_json['spatialCoverage']['geo']['box']
    if 'temporalCoverage' in schemaorg_json:
        detail['temporal_coverage'] = schemaorg_json['temporalCoverage']

    print(f"[file_detail] detail={detail}")
    title = schemaorg_json['name']

    context = {'title': title,
               'detail': detail,
               'schemaorg_json': json.dumps(subject)
               }
    return render(request, get_template(index, 'schema-org-index/detail-overview.html'), context)


def update_site_domain():
    # Site = apps.get_model("sites", "Site")
    try:
        site = Site.objects.get(id=1)
        # host = getattr(settings, "SITE_NAME", None)
        host = os.environ.get('SITE_NAME', 'localhost:8000')
        print(f"[update_site_domain] host={host}")
        site.domain = host
        site.name = host
        site.save()

    except:
        pass


def update_social_app():
    try:
        site = Site.objects.get(id=1)
        # host = getattr(settings, "SITE_NAME", None)
        host = os.environ.get('SOCIAL_APP_cilogon', 'localhost:8000')
        print(f"[update_site_domain] host={host}")
        site.domain = host
        site.name = host
        site.save()

    except:
        pass


def set_django_configurations():
    update_site_domain()
    update_social_app()


set_django_configurations()


def index_selection(request):
    print(f"[index_selection] request={request}")

    context = {
        'search_indexes': get_setting('SEARCH_INDEXES'),
        'allowed_groups': getattr(settings,
                                  'SOCIAL_AUTH_GLOBUS_ALLOWED_GROUPS', [])
    }
    return render(request, 'index-selection.html',
                  context)


def temp_view(request):
    return render(request, 'schema-org-index/detail-overview.html', {})


def site(request):
    return {
        'site': SimpleLazyObject(lambda: get_current_site(request)),
    }


class GetAccountProfile(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, 'error.html', {})
        user = request.user
        # print(f"[GetAccountProfile] user={user.socialaccount_set}")
        # cilogon_account = request.user.socialaccount_set.filter(provider='cilogon').first()
        #
        # cilogon_access_token = cilogon_account.socialtoken_set.filter(token_type='access_token').first().token
        # cilogon_refresh_token = cilogon_account.socialtoken_set.filter(token_type='refresh_token').first().token
        # print(f"[GetAccountProfile] cilogon_access_token={cilogon_access_token}")
        # print(f"[GetAccountProfile] cilogon_refresh_token={cilogon_refresh_token}")

        context = {'username': request.user}
        return render(request, 'account/profile.html', context)


class VerifyTokenRequest(serializers.Serializer):
    header_token = serializers.CharField()
    pass


class VerifyToken(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description='Authentication token',
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ], )
    def get(self, request):
        authorization_header = request.headers.get('Authorization')
        if not authorization_header or not authorization_header.startswith('Bearer '):
            return HttpResponseBadRequest('Invalid Authorization header')
        access_token = authorization_header[len('Bearer '):]
        userinfo = requests.post(
            'https://cilogon.org/oauth2/userinfo',
            data={
                'access_token': access_token,
            },
        )

        if not userinfo.ok:
            return HttpResponseBadRequest('Failed to verify token')

        userinfo_data = userinfo.json()
        print(f"[GetResourceSchemaorg] userinfo_data={userinfo_data}")

        return Response(
            data={"status": "OK", "userinfo": userinfo_data},
            status=status.HTTP_200_OK,
        )


class GetDomainName(View):
    def get(self, request, *args, **kwargs):
        site = Site.objects.get(id=1)
        return site.domain
