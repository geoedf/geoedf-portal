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
from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import SimpleLazyObject

from myportal.constants import GLOBUS_INDEX_NAME


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


class GetDomainName(View):
    def get(self, request, *args, **kwargs):
        site = Site.objects.get(id=1)
        return site.domain


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
