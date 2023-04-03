import json

import coreapi

client = coreapi.Client()

url = 'https://fairshake.cloud/'

schema = client.get('https://fairshake.cloud/coreapi/')
# retrieve local personal access token
from pathlib import Path

TOKEN = Path('FAIRSHAKE_TOKEN').read_text().strip()
params = {'access_token': TOKEN}
client = coreapi.Client(auth=coreapi.auth.TokenAuthentication(token=TOKEN, scheme='token'))
# schema = client.get('https://fairshake.cloud/coreapi/')


# We can test that it worked by reading information about the logged in user.
client.action(
    schema,
    ['auth', 'user', 'read'],
)

# Get FAIRShake rubric
rubric = client.action(schema, ['rubric', 'list'], params={'title': 'PresQT FAIRshare Rubric'})['results']
rubric_id = rubric[0]['id']
metrics = rubric[0]['metrics']
print(json.dumps(metrics))
# Create a project that contains that object
proj = client.action(schema, ['project', 'create'], params=dict(
    url='http://my-objects.com',
    title='My Project',
    description='Project is great',
    tags='my project test',
))
proj_id = proj['id']
print(json.dumps(proj))

# Create a digital object that belongs to that project
obj = client.action(schema, ['digital_object', 'create'], params=dict(
    url='http://my-objects.com/00001',
    title='My Object',
    description='Object is great',
    tags='my object test',
    type='tool',
    rubrics=[rubric_id],
    projects=[proj_id]
))
obj_id = obj['id']

# TODO: the code below creates a score for a certain metric. But I want to run code that produces this score for me
# API at https://fairshake.cloud/coreapi/#
# Create an assessment
client.action(schema, ['assessment', 'create'], params=dict(
    project=proj_id,
    target=obj_id,
    rubric=rubric_id,
    methodology='test',
    answers=[
        {
            'metric': metrics[0],
            'answer': 1.0,
            'url_comment': 'http://my_url.com',
        },
    ],
))
score = client.action(schema, ['score', 'list'], params=dict(target=obj_id))

# import json
# from IPython.display import display, HTML
# HTML("""
# <div
#     id="insignia"
#     data-target="%s"
#     style="width: 40px; height: 40px; border: 0px solid black" />
# """ % (obj_id))
