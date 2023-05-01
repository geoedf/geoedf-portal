import requests
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from globus_portal_framework import post_search
from globus_portal_framework.apps import get_setting


def verify_cilogon_token(access_token):
    userinfo = requests.post(
        'https://cilogon.org/oauth2/userinfo',
        data={
            'access_token': access_token,
        },
    )

    if not userinfo.ok:
        return None
    return userinfo.json()


def get_domain_name():
    site = Site.objects.get(id=1)
    return site.domain


def get_resource_id_list():
    query = get_setting('DEFAULT_QUERY')
    # filters = get_search_filters()
    id_list = []

    for page in range(1,2):

        search_result = post_search('schema-org-index', query, [], AnonymousUser(),
                                    page)  # todo replace index with variable
        print(f'[GeoFileSitemap | items] search_result={search_result}')


        for subject_data in search_result['search_results']:
            # print(f'[GeoFileSitemap | items] subject_data={subject_data["subject"]}')
            # print(f'[GeoFileSitemap | items] subject_data={subject_data}')

            id_list.append(subject_data['subject'])
            print('[get_resource_id_list]' + subject_data['subject'])

    return id_list
