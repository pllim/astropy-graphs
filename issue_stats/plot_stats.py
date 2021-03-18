import sys
from datetime import datetime as dt

import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
import requests
from bs4 import BeautifulSoup

if sys.argv[1:]:
    start_date = float(sys.argv[1])
else:
    start_date = 2011.75

plt.rc('axes', titlesize='medium')
plt.rc('axes', labelsize='medium')
plt.rc('xtick', labelsize='small')
plt.rc('ytick', labelsize='small')
plt.rc('xtick.major', size=2)
plt.rc('ytick.major', size=2)
plt.rc('xtick.minor', size=1)
plt.rc('ytick.minor', size=1)
plt.rc('font', family='serif')
plt.rc('axes', linewidth=0.5)
plt.rc('patch', linewidth=0.5)

# TODO: This might need fixing after the switch to towncrier?
changelog = requests.get('https://docs.astropy.org/en/stable/changelog.html')
soup = BeautifulSoup(changelog.text, 'html5lib')

releases = {}
for entry in soup.findAll('h2'):
    version, date = entry.text.split()
    date = date.split("(")[1].split(")")[0]
    if date == 'unreleased':
        releases[version] = dt.today()
    else:
        releases[version] = dt.strptime(date, "%Y-%m-%d")

feature_freezes = {'4.2 ff': dt(2020, 10, 23),
                   '4.1 ff': dt(2020, 4, 24),
                   '4.0 ff': dt(2019, 10, 25),
                   '3.2 ff': dt(2019, 4, 19),
                   '3.1 ff': dt(2018, 10, 26),
                   '3.0 ff': dt(2017, 12, 24),
                   '2.0 ff': dt(2017, 6, 27),
                   '1.3 ff': dt(2016, 12, 7)}

pyastro_day2 = {'PiA20': dt(2020, 4, 21),
                'PiA19': dt(2019, 7, 30),
                'PiA18': dt(2018, 5, 1),
                'PiA17': dt(2017, 5, 9),
                'PiA16': dt(2016, 3, 22),
                'PiA15': dt(2015, 4, 21)}


def to_year_fraction(date):

    import time

    def sinceEpoch(date):  # returns seconds since epoch
        return time.mktime(date.timetuple())
    s = sinceEpoch

    year = date.year
    startOfThisYear = dt(year=year, month=1, day=1)
    startOfNextYear = dt(year=year+1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed/yearDuration

    return date.year + fraction


def plot_lines(calendar, color='k', alpha=0.8, text_loc=5):

    for event, date in calendar.items():
        year_fraction = to_year_fraction(date)
        if year_fraction > start_date:
            if event.count(".") < 2:
                ax.axvline(year_fraction, color=color, lw=1, alpha=alpha)
                ax.text(year_fraction - 0.01, text_loc, event,
                        rotation=90, ha='right', size=10)
            else:
                ax.axvline(year_fraction, color=color, lw=1, alpha=alpha * 0.3)


created = []
for line in open('created.txt'):
    date = dateutil.parser.parse(line)
    day_of_year = to_year_fraction(date)
    created.append(day_of_year)
created = np.array(created)
created.sort()
created_n = np.arange(len(created)) + 1.

closed = []
for line in open('closed.txt'):
    date = dateutil.parser.parse(line)
    day_of_year = to_year_fraction(date)
    closed.append(day_of_year)
closed = np.array(closed)
closed.sort()
closed_n = np.arange(len(closed)) + 1.

dates = np.hstack([created, closed])
diffs = np.hstack([np.repeat(1, len(created)), np.repeat(-1, len(closed))])

order = np.argsort(dates)

dates = dates[order]
diffs = diffs[order]
total = np.cumsum(diffs)


fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(dates, total, color='blue', lw=2, label='open')
ax.xaxis.set_ticks([2011, 2012, 2013, 2014, 2015, 2016,
                    2017, 2018, 2019, 2020, 2021])
ax.legend(loc='center right', fontsize=11)
ax.xaxis.set_ticklabels(['2011', '2012', '2013', '2014', '2015', '2016',
                         '2017', '2018', '2019', '2020', '2021'])

lower_total = np.min(total[dates > start_date])
lower_closed = np.min(closed_n[closed > start_date])

plot_lines(releases, text_loc=lower_total)
plot_lines(feature_freezes, color='red', alpha=0.6, text_loc=lower_total)
plot_lines(pyastro_day2, color='green', text_loc=lower_total)

ax.set_xlabel("Time")
ax.set_ylabel("Number of issues")
ax.set_title("Astropy issues and PRs")
ax.set_xlim(start_date, np.max(created))
ax.set_ylim(lower_total * 0.98, np.max(total) * 1.02)
fig.savefig('issue_open_stats.png', dpi=150)

ax.plot(closed, closed_n, color='green', lw=2, label='closed')
ax.set_ylim(lower_closed * 0.98, np.max(closed_n) * 1.02)
ax.legend(loc='center left', fontsize=11)
fig.savefig('issue_closed_stats.png', dpi=150)

ax.plot(created, created_n, color='red', lw=2, label='total')
ax.autoscale(axis='y')

ax.legend(loc='center left', fontsize=11)
fig.savefig('issue_stats.png', dpi=150)
