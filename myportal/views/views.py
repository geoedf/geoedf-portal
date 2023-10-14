import csv
import datetime
import json
import os

import requests
from allauth.socialaccount.models import SocialToken
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse, Http404
from django.views import View
from drf_yasg import openapi
from globus_portal_framework import gsearch
from globus_portal_framework.apps import get_setting
from globus_portal_framework.gsearch import post_search, get_search_query, get_search_filters, get_template, \
    get_subject, get_index
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import SimpleLazyObject

from myportal.constants import GLOBUS_INDEX_NAME, FILES_ROOT
from myportal.utils import generate_nested_directory
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage


def mysearch(request, index):
    query = get_search_query(request)
    # print(f'[mysearch]{query}')
    filters = get_search_filters(request)
    print(f"[mysearch] user={AnonymousUser()}")
    print(f"[mysearch] user={request.user}")

    search_result = post_search(GLOBUS_INDEX_NAME, query, filters, AnonymousUser(),
                                request.GET.get('page', 1))
    print(f'[mysearch]search_result = {search_result}')
    context = {'search': search_result}
    return render(request, get_template(index, 'schema-org-index/components/search-results.html'), context)


def file_detail(request, uuid):
    index = GLOBUS_INDEX_NAME
    subject = get_subject(index, uuid, AnonymousUser())
    print(f"[file_detail] subject={subject}")
    try:
        endpoint = subject['all'][0]
    except KeyError:
        context = {
            "error": {
                "code": 500,
                "msg": "Unable to fetch the resource. Please check if the resource id exists."
            }
        }
        return render(request, get_template(index, 'error.html'), context)

    schemaorg_json = endpoint['schemaorgJson']

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

    # print(f"[file_detail] detail={detail}")

    title = schemaorg_json['name']

    context = {'title': title,
               'detail': detail,
               'schemaorg_json': json.dumps(schemaorg_json, indent=4)
               }

    # print(f"[file_detail] schemaorg_json={context['schemaorg_json']}")

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
        print(f"[update_social_app] host={host}")
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


class GetDomainName(View):
    def get(self, request, *args, **kwargs):
        site = Site.objects.get(id=1)
        print(f"[GetDomainName] site.domain={site.domain}")
        data = {'domain': site.domain}
        return JsonResponse(data)


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


class FileManager(View):
    def get_breadcrumbs(self, request):
        path_components = [component for component in request.path.split("/") if component]
        breadcrumbs = []
        url = ''

        for component in path_components:
            url += f'/{component}'
            if component == "file-manager":
                component = "media"
            breadcrumbs.append({'name': component, 'url': url})

        return breadcrumbs

    def convert_csv_to_text(self, csv_file_path):
        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)

        text = ''
        for row in rows:
            text += ','.join(row) + '\n'

        return text

    def get_files_from_directory(self, directory_path):
        files = []
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                try:
                    print(' > file_path ' + file_path)
                    _, extension = os.path.splitext(filename)
                    if extension.lower() == '.csv':
                        csv_text = self.convert_csv_to_text(file_path)
                    else:
                        csv_text = ''

                    last_modified_time = os.path.getmtime(file_path)
                    file_size = os.path.getsize(file_path)
                    print("os.sep" + os.sep)
                    files.append({
                        'file': file_path.split(os.sep + 'files' + os.sep)[1],
                        'filename': filename,
                        'file_path': file_path,
                        'visibility': 'private',
                        'last_modified_time': datetime.datetime.fromtimestamp(last_modified_time),
                        'size': file_size,
                        'csv_text': csv_text
                    })
                except Exception as e:
                    print(' > ' + str(e))
        return files

    def get(self, request, directory=FILES_ROOT, *args, **kwargs):
        media_path = os.path.join(FILES_ROOT)

        directories = generate_nested_directory(media_path, media_path)
        selected_directory = directory

        files = []
        selected_directory_path = os.path.join(media_path, selected_directory)
        if os.path.isdir(selected_directory_path):
            files = self.get_files_from_directory(selected_directory_path)

        breadcrumbs = self.get_breadcrumbs(request)
        context = {
            'directories': directories,
            'files': files,
            'selected_directory': selected_directory,
            'segment': 'file_manager',
            'breadcrumbs': breadcrumbs
        }
        print(context)
        return render(request, 'file-management/file-manager.html', context)


def delete_file(request, file_path):
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    os.remove(absolute_file_path)
    print("File deleted", absolute_file_path)
    return redirect(request.META.get('HTTP_REFERER'))


def download_file(request, file_path):
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(absolute_file_path):
        with open(absolute_file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(absolute_file_path)
            return response
    raise Http404


def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage(location='data/files/idata_files')  # saves to the 'files' directory under MEDIA_ROOT
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)  # You can get the file URL if needed

    context = {
        "msg": f"Upload success, directory{file_url}"
    }
    return redirect(request.META.get('HTTP_REFERER'))


def save_info(request, file_path):
    path = file_path.replace('%slash%', '/')
    # if request.method == 'POST':
    #     FileInfo.objects.update_or_create(
    #         path=path,
    #         defaults={
    #             'info': request.POST.get('info')
    #         }
    #     )

    return redirect(request.META.get('HTTP_REFERER'))
