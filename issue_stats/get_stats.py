import os
import time

import requests

try:
    token = os.environ['GITHUB_TOKEN']
except KeyError:
    raise KeyError('GITHUB_TOKEN environment variable is not set') from None

session = requests.Session()
session.headers['Authorization'] = f'token {token}'

auth = session.get('https://api.github.com')
auth.raise_for_status()

BASE_URL = "https://api.github.com/repos/astropy/astropy/issues"

created = []
closed = []

params = {}
params['per_page'] = 100

params['state'] = 'closed'
params['page'] = 1

while True:

    response = session.get(BASE_URL, params=params)
    if response.status_code == 403:
        print('.', end='')
        time.sleep(1)
        continue
    response.raise_for_status()
    results = response.json()

    if len(results) == 0:
        break

    for issue in results:
        created.append(issue['created_at'])
        closed.append(issue['closed_at'])

    print(f"Retrieved page {params['page']} of closed issues")
    params['page'] += 1
    # slow it down so we don't exceed the rate limit imposed by the API
    time.sleep(1)

params['state'] = 'open'
params['page'] = 1

while True:

    response = session.get(BASE_URL, params=params)
    if response.status_code == 403:
        print('.', end='')
        time.sleep(1)
        continue
    response.raise_for_status()
    results = response.json()

    if len(results) == 0:
        break

    for issue in results:
        created.append(issue['created_at'])

    print(f"Retrieved page {params['page']} of open issues")
    params['page'] += 1
    # slow it down so we don't exceed the rate limit imposed by the API
    time.sleep(1)

with open('created.txt', 'w') as f:
    for c in created:
        f.write(c + '\n')

with open('closed.txt', 'w') as f:
    for c in closed:
        f.write(c + '\n')
