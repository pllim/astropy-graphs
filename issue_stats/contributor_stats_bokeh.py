from collections import Counter

import numpy as np
from astropy.io import ascii
from astropy.table import Table

from bokeh.layouts import row
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show

tbl = Table.read(
    'astropy_issue_states.csv', format='ascii.csv',
    converters={'Issue Number': [ascii.convert_numpy(np.int)],
                'State': [ascii.convert_numpy(np.str)],
                'Creation Date': [ascii.convert_numpy(np.datetime64)],
                'Close Date': [ascii.convert_numpy(np.str)],  # datetime when valid  # noqa
                'Labels': [ascii.convert_numpy(np.str)],
                'Is_PR': [ascii.convert_numpy(np.bool)],
                'Creator': [ascii.convert_numpy(np.str)],
                'Asignees': [ascii.convert_numpy(np.str)],
                'Lifetime': [ascii.convert_numpy(np.float)]  # timedelta in s
                })

is_pr = tbl['Is_PR']
data = {'year': [],
        'n_issue_authors': [],
        'n_pr_authors': []}

for year in range(2010, 2022):
    min_t = np.datetime64(f'{year}-01-01')
    max_t = np.datetime64(f'{year + 1}-01-01')
    created = tbl['Creation Date']
    mask = (created >= min_t) & (created < max_t)
    data['year'].append(year)

    issues = tbl[mask & ~is_pr]
    data['n_issue_authors'].append(len(set(issues['Creator'])))

    prs = tbl[mask & is_pr]
    data['n_pr_authors'].append(len(set(prs['Creator'])))

data = ColumnDataSource(data)
TOOLTIPS = [
    ("Year", "@year"),
    ("# Issue authors", "@n_issue_authors"),
    ("# PR authors", "@n_pr_authors")]

p = figure(title='Number of authors', x_range=(2010, 2022),
           background_fill_color="#fafafa", tooltips=TOOLTIPS)
p.vbar(x="year", top="n_issue_authors", width=0.9, color="#9A44B6",
       source=data, legend_label="Issues")
p.vbar(x="year", top="n_pr_authors", width=0.9, color="#338ADD",
       fill_alpha=0.5, source=data, legend_label="PRs")

p.y_range.start = 0
p.yaxis.axis_label = '#'
p.xgrid.grid_line_color = None
p.outline_line_color = None
p.legend.click_policy = "hide"
p.legend.location = "top_left"

unique_authors = sorted(set(tbl['Creator']))  # Does not account for dup acc.
issues_by_author = []
prs_by_author = []
logbins = [0, 5, 10, 20, 30, 40, 50, 100, 150, 200, 250, 300, 350, 400, 450,
           500, 1000]
recent = tbl['Creation Date'] > np.datetime64('2018-03-19')  # Last 3 years
issue_counter = Counter()
pr_counter = Counter()

for user in unique_authors:
    mask = tbl['Creator'] == user

    issues = tbl[recent & mask & ~is_pr]
    n1 = len(issues)
    issues_by_author.append(n1)
    issue_counter[user] += n1

    prs = tbl[recent & mask & is_pr]
    n2 = len(prs)
    prs_by_author.append(n2)
    pr_counter[user] += n2

hist_issues, edges_issues = np.histogram(issues_by_author, density=False,
                                         bins=logbins)
hist_prs, edges_prs = np.histogram(prs_by_author, density=False,
                                   bins=logbins)

p2 = figure(title="Number of issues and PRs by authors (last 3 years)",
            background_fill_color="#efefef", tooltips=[("(x,y)", "($x, $y)")])
p2.quad(top=hist_issues, bottom=0,
        left=edges_issues[:-1], right=edges_issues[1:],
        fill_color="#9A44B6", line_color="white",
        legend_label="Issues")
p2.quad(top=hist_prs, bottom=0,
        left=edges_prs[:-1], right=edges_prs[1:],
        fill_color="#338ADD", line_color="white", fill_alpha=0.5,
        legend_label="PRs")
p2.y_range.start = 0
p2.y_range.end = 30
p2.yaxis.axis_label = '# Authors'
p2.xaxis.axis_label = '# Issues/PRs'
p2.legend.click_policy = "hide"
p2.legend.location = "top_right"

show(row(p, p2))

# Maybe can put in slide... not sure
print('Issues')
print(issue_counter.most_common(25))
print()
print('PRs')
print(pr_counter.most_common(25))