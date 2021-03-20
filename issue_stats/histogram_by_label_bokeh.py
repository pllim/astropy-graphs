import numpy as np
import pandas as pd
from astropy.io import ascii
from astropy.table import Table

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

# Flags
is_pr = tbl['Is_PR']
is_open = tbl['State'] != 'closed'

labels = ['config', 'constants', 'convolution', 'coordinates', 'cosmology',
          'io.ascii', 'io.fits', 'io.misc', 'io.misc.asdf', 'io.registry',
          'io.votable', 'logging', 'modeling', 'nddata', 'samp', 'stats',
          'table', 'testing', 'time', 'timeseries', 'uncertainty',
          'unified-io', 'units', 'utils', 'utils.iers', 'visualization',
          'visualization.wcsaxes', 'wcs', 'wcs.wcsapi']
n_prs = []
n_issues = []
n_issues_bugs = []

for label in labels:
    has_label = []
    has_label_and_bug = []
    for row in tbl:
        cell = row['Labels']
        if cell:
            row_labels = cell.split(',')
            found = label in row_labels
            has_label.append(found)
            has_label_and_bug.append(found & ('Bug' in row_labels))
        else:
            has_label.append(False)
            has_label_and_bug.append(False)

    has_label = np.array(has_label, dtype=np.bool)
    has_label_and_bug = np.array(has_label_and_bug, dtype=np.bool)

    # Number of open PRs and issues with that label
    n_prs.append(np.count_nonzero(has_label & is_pr & is_open))
    n_issues.append(np.count_nonzero(has_label & ~is_pr & is_open))
    n_issues_bugs.append(np.count_nonzero(
        has_label_and_bug & ~is_pr & is_open))

# Shorten label for display
labels[labels.index('visualization.wcsaxes')] = 'wcsaxes'

data = ColumnDataSource({'labels': labels,
                         'Issues_all': n_issues,
                         'Issues_bug': n_issues_bugs,
                         'PRs': n_prs})

# Print some stats
df = pd.DataFrame.from_dict({'labels': labels,
                             'Issues_all': n_issues,
                             'Issues_bug': n_issues_bugs,
                             'PRs': n_prs})
df['Bug_ratio'] = df['Issues_bug'] / df['Issues_all']
print('Top 5 most issues')
print(df.nlargest(5, 'Issues_all'))
print()
print('Top 3 most bug ratio')
print(df.nlargest(3, 'Bug_ratio'))
print()
print('Top 5 most PRs')
print(df.nlargest(5, 'PRs'))

TOOLTIPS = [
    ("Label", "@labels"),
    ("# Issues (all)", "@Issues_all"),
    ("# Issues (bug)", "@Issues_bug"),
    ("# PRs", "@PRs")]

p = figure(title='Open issues/PRs by subpackage', x_range=labels,
           plot_width=800, background_fill_color="#fafafa", tooltips=TOOLTIPS)
p.vbar(x="labels", top="Issues_all", width=0.9, color="#9A44B6",
       source=data, legend_label="Issues (all)")
p.vbar(x="labels", top="Issues_bug", width=0.9, color="#A60628",
       fill_alpha=0.75, source=data, legend_label="Issues (bug)")
p.vbar(x="labels", top="PRs", width=0.9, color="#338ADD", fill_alpha=0.5,
       source=data, legend_label="PRs")

p.y_range.start = 0
p.yaxis.axis_label = '#'
p.x_range.range_padding = 0.1
p.xaxis.major_label_orientation = np.pi / 2
p.xaxis.major_label_text_font_size = "18pt"
p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None
p.legend.click_policy = "hide"
p.legend.location = "top_right"

show(p)
