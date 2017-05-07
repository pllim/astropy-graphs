import numpy as np
import json
import time
from six.moves import input
from astropy.table import Table
from datetime import datetime

import requests

session = requests.Session()

username = input('Username: ')

try:
    import getpass
    import keyring
    pw = keyring.get_password('api.github.com', username)
    if pw is None:
        pw = getpass.getpass(prompt='Password for api.github.com: ')
        keyring.set_password('api.github.com', username, pw)
except ImportError:
    password = input('Password (plaintext - if you want to hide it, install getpass & keyring): ')

authorization = (username, pw)
auth = session.get('https://api.github.com', auth=authorization)
auth.raise_for_status()

BASE_URL = "https://api.github.com/repos/astropy/astropy/issues"

params = {}
params['per_page'] = 100

params['page'] = 1
params['state'] = 'all'

tformat = "%Y-%m-%dT%H:%M:%SZ"

tbl = Table(names=['Issue Number', 'State', 'Creation Date', 'Close Date', 'Labels', 'Is_PR', 'Creator', 'Asignees', 'Lifetime'],
            dtype=[int, 'S6', 'S20', 'S20', 'S100', bool, 'S20', 'S100', np.timedelta64(1,'s')])

while True:

    response = session.get(BASE_URL, params=params, auth=authorization)
    if response.status_code == 403:
        print('.', end='')
        time.sleep(1)
        continue
    response.raise_for_status()
    results = response.json()

    if len(results) == 0:
        break

    for issue in results:

        lifetime = ((datetime.strptime(issue['closed_at'], tformat) if
                     'closed_at' in issue and issue['closed_at'] is not None
                     else datetime.today()) -
                    datetime.strptime(issue['created_at'], tformat)).total_seconds()

        tbl.add_row([issue['number'],
                     issue['state'],
                     issue['created_at'],
                     issue['closed_at'] if 'closed_at' in issue else 'open',
                     ",".join([label['name'] for label in issue['labels']]),
                     'pull_request' in issue,
                     issue['user']['login'],
                     (",".join([assignee['login'] for assignee in
                                issue['assignees']]) if issue['assignees']
                      else ""),
                     lifetime*np.timedelta64(1, 's'),
                    ])


    params['page'] += 1
    print("Retrieved page {0} of all issues".format(params['page']))
    # slow it down so we don't exceed the rate limit imposed by the API
    time.sleep(1)

tbl.write('astropy_issue_states.txt', format='ascii.fixed_width')
