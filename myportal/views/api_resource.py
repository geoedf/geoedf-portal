from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseBadRequest
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from globus_portal_framework import get_subject
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from rest_framework.views import APIView

from myportal.constants import GLOBUS_INDEX_NAME
from myportal.utils import verify_cilogon_token


class GetResourceSchemaorgRequest(serializers.Serializer):
    # id = serializers.IntegerField()
    pass


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
    ], )
    def post(self, request, uuid):

        print(f"[GetResourceSchemaorg] user={request.user}")
        if not has_valid_cilogon_token(request.headers):
            return Response(
                data={"status": "Please log in first"},
                status=status.HTTP_200_OK,
            )
        serializer = GetResourceSchemaorgRequest(data=request.data)
        if serializer.is_valid():
            subject = get_subject(GLOBUS_INDEX_NAME, uuid, AnonymousUser())
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
        if not has_valid_cilogon_token(request.headers):
            return Response(
                data={"status": "Please log in first"},
                status=status.HTTP_200_OK,
            )

        serializer = GetResourceSchemaorgRequest(data=request.data)
        if serializer.is_valid():
            subject = get_subject(GLOBUS_INDEX_NAME, request.id_list, request.user)  # todo
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


def has_valid_cilogon_token(headers):
    authorization_header = headers.get('Authorization')
    if not authorization_header or not authorization_header.startswith('Bearer '):
        return HttpResponseBadRequest('Invalid Authorization header')
    access_token = authorization_header[len('Bearer '):]
    if verify_cilogon_token(access_token) is None:
        return False
    return True
