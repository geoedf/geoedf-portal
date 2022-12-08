import os
from django.contrib.sites.models import Site
from django.shortcuts import render
from globus_portal_framework.gsearch import post_search, get_search_query, get_search_filters, get_template, \
    get_subject, get_index


def update_site_domain():
    # Site = apps.get_model("sites", "Site")
    site = Site.objects.get(id=1)
    host = os.environ.get("SITE_HOST", default="localhost:8000")  # todo get host name

    site.domain = host
    site.name = host
    site.save()


update_site_domain()


def mysearch(request, index):
    query = get_search_query(request)
    print(f'[mysearch]{query}')
    filters = get_search_filters(request)
    search_result = post_search(index, query, filters, request.user,
                                request.GET.get('page', 1))
    print(f'[mysearch]search_result = {search_result}')
    context = {'search': search_result}
    return render(request, get_template(index, 'schema-org-index/components/search-results.html'), context)


def file_detail(request, index, uuid):
    subject = get_subject(index, uuid, request.user)
    print(f"[file_detail] subject={subject}")

    endpoint = subject['all'][0]

    schemaorg_json = endpoint['schemaorgJson']
    print("***")
    print(f"[file_detail] schemaorg_json={schemaorg_json}")

    detail = {'id': schemaorg_json['@id'],
              'subject': subject['subject'],
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
               'schemaorg_json': subject
               }
    return render(request, get_template(index, 'schema-org-index/detail-overview.html'), context)
