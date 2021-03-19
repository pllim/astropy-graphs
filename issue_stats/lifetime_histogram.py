import matplotlib.pyplot as plt
import numpy as np
from astropy.io import ascii
from astropy.table import Table
from astropy.utils.console import ProgressBar

plt.rcParams['axes.prop_cycle'] = plt.cycler('color', ('#338ADD', '#9A44B6',
                                                       '#A60628', '#467821',
                                                       '#CF4457', '#188487',
                                                       '#E24A33'))

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

lifetime = tbl['Lifetime']
is_pr = tbl['Is_PR']
is_closed = tbl['State'] == 'closed'

unique_labels = list(set([x for row in tbl
                          for x in str(row['Labels']).split(",")]))

plt.figure(1).clf()
logdaybins = np.logspace(1 - 5, 8.25 - 5)
plt.hist(lifetime[is_closed] / 86400, bins=logdaybins,
         label='All Closed Issues')
plt.hist(lifetime[np.logical_and(is_closed, is_pr)] / 86400, bins=logdaybins,
         label='Closed PRs')

plt.xscale('log')
plt.xlabel("Lifetime (days)")
plt.legend(loc='best')
plt.savefig("issue_lifetime_closed.png")

plt.figure(1).clf()
logdaybins = np.logspace(1 - 5, 8.25 - 5)
plt.hist(lifetime / 86400, bins=logdaybins, label='All Issues')
plt.hist(lifetime[is_pr] / 86400, bins=logdaybins, label='PRs')

plt.xscale('log')
plt.xlabel("Lifetime (days)")
plt.legend(loc='best')
plt.savefig("issue_lifetime_full.png")

plt.figure(2).clf()
plt.hist(lifetime / 3600, bins=np.linspace(0, 48, 49), label='All Issues')
plt.hist(lifetime[is_pr] / 3600, bins=np.linspace(0, 48, 49), label='PRs')
plt.xlabel("Lifetime (hours)")
plt.legend(loc='best')
plt.savefig("issue_lifetime_short.png")

lifetimes = []
for label in ProgressBar(unique_labels):
    mask = np.array([label in str(row['Labels']) for row in tbl], dtype='bool')
    lifetimes.append(lifetime[mask])

plt.figure(3).clf()
cmap = plt.cm.get_cmap("Spectral")
colors = cmap(np.linspace(0, 1, len(unique_labels)))

plt.hist(lifetimes, bins=np.logspace(1, 8.25, 50), label=unique_labels,
         stacked=True, color=colors)
plt.xscale('log')

plt.xlabel("Lifetime (hours)")
plt.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
plt.savefig("issue_lifetime_labeled.png", bbox_inches='tight')
