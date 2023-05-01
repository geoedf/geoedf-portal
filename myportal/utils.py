import requests
from django.contrib.sites.models import Site


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