import json

import globus_sdk
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from globus_portal_framework.gsearch import post_search, get_search_query, get_search_filters, get_template, get_subject, get_index
# import schemaorg

def mysearch(request, index):
    print("[mysearch]")
    query = get_search_query(request)
    print(f'[mysearch]{query}')
    filters = get_search_filters(request)
    search_result = post_search(index, query, filters, request.user,
                                     request.GET.get('page', 1))
    print(f"search_result = {search_result}")
    context = {'search': search_result}
    return render(request, get_template(index, 'schema-org-index/components/search-results.html'), context)


def file_detail(request, index, uuid):
    subject = get_subject(index, uuid, request.user)
    print(f"[file_detail] subject={subject}")

    endpoint = subject['all'][0]

    schemaorg_json = endpoint['schemaorgJson']
    # except :
    #     return render(request, get_template(index, 'schema-org-index/detail-overview.html'), context)
    detail = {}
    # client_response = globus_sdk.SearchClient.get_subject(index, uuid)
    print("***")
    print(f"[file_detail] schemaorg_json={schemaorg_json}")


    detail = {'id': schemaorg_json['@id'],
              'subject': subject['subject'],
              'creator': schemaorg_json['creator']['@list'][0]['name'],
              }
    if 'spatialCoverage' in schemaorg_json:
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
    # print(f'[mysearch]{json.dumps(context, indent=4, sort_keys=True, default=str)}')
    return render(request, get_template(index, 'schema-org-index/detail-overview.html'), context)
