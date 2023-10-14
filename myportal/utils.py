import os
import uuid

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
    id_list = []

    page = 1
    has_more = True
    while has_more:
        search_result = post_search('list-search-index', query, [], AnonymousUser(),
                                    page)
        for subject_data in search_result['search_results']:
            id_list.append(subject_data['subject'])
        if len(search_result['pagination']['pages']) > page:
            page += 1
        else:
            has_more = False

    print(f'[get_resource_id_list] id_list={id_list}')
    return id_list


def generate_nested_directory(root_path, current_path):
    directories = []
    for name in os.listdir(current_path):
        if os.path.isdir(os.path.join(current_path, name)):
            unique_id = str(uuid.uuid4())
            nested_path = os.path.join(current_path, name)
            nested_directories = generate_nested_directory(root_path, nested_path)
            directories.append({'id': unique_id, 'name': name, 'path': os.path.relpath(nested_path, root_path), 'directories': nested_directories})
    return directories
