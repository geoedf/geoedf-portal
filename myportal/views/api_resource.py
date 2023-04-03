import json
import uuid

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseBadRequest
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.utils import swagger_serializer_method
from globus_portal_framework import get_subject
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from rest_framework.views import APIView

from myportal.constants import GLOBUS_INDEX_NAME, RMQ_NAME, RMQ_USER, RMQ_PASS, RMQ_HOST_IP
from myportal.models import Resource
from myportal.utils import verify_cilogon_token
import pika


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


class PublishResourceRequest(serializers.Serializer):
    # id = serializers.IntegerField()
    publication_name = serializers.CharField()
    path = serializers.CharField()
    resource_type = serializers.CharField()
    pass


# class PublishResourceResponseSerializer():
#     # id = serializers.IntegerField()
#     filepath = serializers.CharField()


class PublishResource(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=PublishResourceRequest, manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description='Authentication token',
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ], )
    def post(self, request):
        print(f"[PublishResource] user={request.user}")
        # todo recover login check
        # if not has_valid_cilogon_token(request.headers):
        #     return Response(
        #         data={"status": "Please log in first"},
        #         status=status.HTTP_200_OK,
        #     )
        serializer = PublishResourceRequest(data=request.data)
        if serializer.is_valid():
            file_uuid = str(uuid.uuid4())
            resource = Resource(uuid=file_uuid,
                                path=serializer.validated_data['path'],
                                resource_type=serializer.validated_data['resource_type'])
            resource.save()
            print(f"[PublishResource] resource={resource.__str__()}")

            publish_to_globus_index(resource)
            task_id = get_globus_index_submit_taskid(resource)
            resource.task_id = task_id
            resource.save()
            return Response(
                data={"status": "Submitted", "uuid": file_uuid,
                      "path": serializer.validated_data['path'],
                      "task_id": task_id,
                      },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def publish_to_globus_index(resource):
    credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RMQ_HOST_IP, port=5672, virtual_host='/', credentials=credentials))

    channel = connection.channel()

    channel.queue_declare(queue=RMQ_NAME)

    # Send the message to the queue
    message = json.dumps({
        "uuid": resource.uuid,
        "type": resource.resource_type,
        "path": resource.path,
    })
    # todo get task id

    channel.basic_publish(exchange='',
                          routing_key=RMQ_NAME,
                          body=message.encode("utf-8"))
    # body=json.dumps(message).encode("utf-8"))

    # Close the connection
    connection.close()


def get_globus_index_submit_taskid(resource):
    # "d03eb370-49a9-4d59-8791-5bcf9635d65a"
    return uuid.uuid4()


class GetResourceStatusRequest(serializers.Serializer):
    # id = serializers.IntegerField()
    uuid = serializers.CharField()
    pass


class GetResourceStatus(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=GetResourceStatusRequest, manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description='Authentication token',
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ], )
    def post(self, request):
        print(f"[GetResourceStatus] user={request.user}")
        # if not has_valid_cilogon_token(request.headers):
        #     return Response(
        #         data={"status": "Please log in first"},
        #         status=status.HTTP_200_OK,
        #     )
        serializer = GetResourceStatusRequest(data=request.data)
        if serializer.is_valid():
            # file_uuid = str(uuid.uuid4())
            uuid = serializer.validated_data['uuid']
            print(f"[GetResourceStatus] uuid={uuid}")
            try:
                resource = Resource.objects.get(uuid=uuid)
            except Exception as e:
                return Response(
                    data={"msg": f"Error info = {e}"},
                    status=status.HTTP_200_OK,
                )

            return Response(
                data={"status": "OK",
                      "uuid": resource.uuid,
                      "file_path": resource.path,
                      # "file_path": serializer.validated_data['path'],
                      "task_id": resource.task_id,
                      "task_status": "tasks completed successfully",
                      },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UpdateResourceRequest(serializers.Serializer):
    uuid = serializers.IntegerField()
    publication_name = serializers.CharField()
    path = serializers.CharField()
    resource_type = serializers.CharField()
    user_id = serializers.CharField()
    pass


class UpdateResource(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=UpdateResourceRequest, manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description='Authentication token',
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ], )
    def post(self, request):
        print(f"[UpdateResource] user={request.user}")

        if not has_valid_cilogon_token(request.headers):
            return Response(
                data={"status": "Please log in first"},
                status=status.HTTP_200_OK,
            )
        serializer = UpdateResourceRequest(data=request.data)
        if serializer.is_valid():
            resource = Resource.objects.get(uuid=serializer.validated_data['uuid'])
            resource.task_id = serializer.validated_data['task_id']
            resource.user_id = serializer.validated_data['user_id']
            resource.save()
            print(f"[UpdateResource] resource={resource.__str__()}")

            return Response(
                data=json.dumps(resource),
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
