import requests


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
