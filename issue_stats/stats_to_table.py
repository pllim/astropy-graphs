import os
import time
from datetime import datetime

import requests

try:
    token = os.environ['GITHUB_TOKEN']
except KeyError:
    raise KeyError('GITHUB_TOKEN environment variable is not set') from None


def get_github_issues_stats():
    today = datetime.today()

    session = requests.Session()
    session.headers['Authorization'] = f'token {token}'

    BASE_URL = "https://api.github.com/repos/astropy/astropy/issues"

    params = {}
    params['per_page'] = 100

    params['page'] = 1
    params['state'] = 'all'

    tformat = "%Y-%m-%dT%H:%M:%SZ"

    colnames = ['Issue Number', 'State', 'Creation Date', 'Close Date',
                'Labels', 'Is_PR', 'Creator', 'Asignees', 'Lifetime']
    rows = []

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

            lifetime = (
                (datetime.strptime(issue['closed_at'], tformat) if
                 'closed_at' in issue and issue['closed_at'] is not None
                 else today) -
                datetime.strptime(issue['created_at'], tformat)).total_seconds()  # noqa

            rows.append([
                str(issue['number']),
                issue['state'],
                issue['created_at'],
                issue['closed_at'] if ('closed_at' in issue and
                                       issue['closed_at']) else 'open',
                f"\"{','.join([label['name'] for label in issue['labels']])}\"",  # noqa
                str('pull_request' in issue),
                issue['user']['login'],
                f"\"{','.join([assignee['login'] for assignee in issue['assignees']]) if issue['assignees'] else ''}\"",  # noqa
                str(lifetime)])

        print(f"Retrieved page {params['page']} of all issues")
        params['page'] += 1
        # slow it down so we don't exceed the rate limit imposed by the API
        time.sleep(1)

    return colnames, rows


if __name__ == '__main__':
    colnames, rows = get_github_issues_stats()

    # NOTE: We write to simple plain-text CSV here because API query is
    # expensive and I don't want to deal with Table API change when this
    # script is only run every 1-2 years.
    # We will load it back into a proper Astropy Table on read, if desired.
    with open('astropy_issue_states.csv', 'w') as fout:
        fout.write(f"{','.join(colnames)}{os.linesep}")
        for row in rows:
            fout.write(f"{','.join(row)}{os.linesep}")
