import time
from datetime import datetime as dt

import numpy as np
import requests
from bs4 import BeautifulSoup

from bokeh.io import show
from bokeh.layouts import column
from bokeh.models import RangeTool, Span, Label
from bokeh.plotting import figure


def read_issue_stats(filename):
    stats = []
    with open(filename) as fin:
        for line in fin:
            stats.append(line.split('T')[0])
    stats.sort()
    return np.array(stats, dtype=np.datetime64)


def find_astropy_releases():
    # TODO: This might need fixing after the switch to towncrier?
    changelog = requests.get(
        'https://docs.astropy.org/en/stable/changelog.html')
    soup = BeautifulSoup(changelog.text, 'html5lib')
    releases = {}
    for entry in soup.findAll('h2'):
        version, date = entry.text.split()
        date = date.split("(")[1].split(")")[0]
        if date == 'unreleased':
            releases[version] = dt.today().strftime('%Y-%m-%d')
        else:
            releases[version] = date
    return releases


# NOTE: Too crowded if we include this, so commented out.
# IMPORTANT_DATES = find_astropy_releases()
IMPORTANT_DATES = {}

IMPORTANT_DATES.update({
    '4.2 ff': '2020-10-23',  # Feature freeze
    '4.1 ff': '2020-04-24',
    '4.0 ff': '2019-10-25',
    '3.2 ff': '2019-04-19',
    '3.1 ff': '2018-10-26',
    '3.0 ff': '2017-12-24',
    '2.0 ff': '2017-06-27',
    '1.3 ff': '2016-12-07',
    'PiA20': '2020-04-21',  # PyAstro Day 2
    'PiA19': '2019-07-30',
    'PiA18': '2018-05-01',
    'PiA17': '2017-05-09',
    'PiA16': '2016-03-22',
    'PiA15': '2015-04-21'
})

ASTROPY_ISSUES_CREATED = read_issue_stats('created.txt')
ASTROPY_ISSUES_CLOSED = read_issue_stats('closed.txt')

# Plot

dates = np.hstack([ASTROPY_ISSUES_CREATED, ASTROPY_ISSUES_CLOSED])
diffs = np.hstack([np.repeat(1, len(ASTROPY_ISSUES_CREATED)),
                   np.repeat(-1, len(ASTROPY_ISSUES_CLOSED))])
order = np.argsort(dates)
dates = dates[order]
diffs = diffs[order]
total = np.cumsum(diffs)

p = figure(plot_height=300, plot_width=800,
           x_axis_type="datetime", x_axis_location="above",
           background_fill_color="#efefef", x_range=(dates[-5000], dates[-1]))
p.line(x=dates, y=total)
p.yaxis.axis_label = "#"

select = figure(title="Astropy issues and PRs",
                plot_height=130, plot_width=800, y_range=p.y_range,
                x_axis_type="datetime", y_axis_type=None,
                tools="", toolbar_location=None,
                background_fill_color="#efefef")

range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

select.line(x=dates, y=total)
select.ygrid.grid_line_color = None
select.add_tools(range_tool)
select.toolbar.active_multi = range_tool

for key, val in IMPORTANT_DATES.items():
    if 'ff' in key:
        color = 'red'
    elif 'PiA' in key:
        color = 'blue'
    else:
        color = 'green'

    t = time.mktime(dt.strptime(val, '%Y-%m-%d').timetuple()) * 1000
    vline = Span(location=t, dimension='height', line_color=color)
    p.renderers.extend([vline, ])
    select.renderers.extend([vline, ])

    vline_label = Label(x=t, y=0, x_units='data', y_units='data',
                        angle=np.pi / 2, text_color=color, text=key)
    p.add_layout(vline_label)

show(column(p, select))
