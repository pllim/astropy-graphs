from collections import defaultdict

import numpy as np
from astropy.io import ascii
from astropy.table import Table

from bokeh.models import ColumnDataSource, HoverTool
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

labels = ['config', 'constants', 'convolution', 'coordinates', 'cosmology',
          'io.ascii', 'io.fits', 'io.misc', 'io.misc.asdf', 'io.registry',
          'io.votable', 'logging', 'modeling', 'nddata', 'samp', 'stats',
          'table', 'testing', 'time', 'timeseries', 'uncertainty',
          'unified-io', 'units', 'utils', 'utils.iers', 'visualization',
          'visualization.wcsaxes', 'wcs', 'wcs.wcsapi']
recent = tbl['Creation Date'] > np.datetime64('2018-03-19')  # Last 3 years
subpkg_counter = defaultdict(dict)

for row in tbl[recent]:
    cell = row['Labels']
    if not cell:
        continue

    is_pr = row['Is_PR']
    author = row['Creator']
    row_labels = cell.split(',')

    for label in row_labels:
        if label not in labels:
            continue

        if author not in subpkg_counter[label]:
            subpkg_counter[label][author] = {'n_issues': 0,
                                             'n_prs': 0}

        if row['Is_PR']:
            subpkg_counter[label][author]['n_prs'] += 1
        else:
            subpkg_counter[label][author]['n_issues'] += 1


def issue_prs_mix_per_subpkg(subpkg):
    only_issues = 0
    only_prs = 0
    both_issues_prs = 0

    for author in subpkg_counter[subpkg]:
        n_issues = subpkg_counter[subpkg][author]['n_issues']
        n_prs = subpkg_counter[subpkg][author]['n_prs']
        if n_issues < 1 and n_prs < 1:
            continue
        if n_issues >= 1:
            if n_prs < 1:
                only_issues += 1
            else:
                both_issues_prs += 1
        else:
            only_prs += 1

    return only_issues, only_prs, both_issues_prs


data = {'only_issues': [], 'only_prs': [], 'both_issues_prs': []}
for label in labels:
    only_issues, only_prs, both_issues_prs = issue_prs_mix_per_subpkg(label)
    data['only_issues'].append(only_issues)
    data['only_prs'].append(only_prs)
    data['both_issues_prs'].append(both_issues_prs)


# Shorten label for display
labels[labels.index('visualization.wcsaxes')] = 'wcsaxes'
data['labels'] = labels
data = ColumnDataSource(data)

TOOLTIPS = [
    ("Label", "@labels"),
    ("# Only open issues", "@only_issues"),
    ("# Only open PRs", "@only_prs"),
    ("# Both", "@both_issues_prs")]

p = figure(title='Contributor types by subpackage (last 3 years)',
           x_range=labels, plot_width=800, background_fill_color="#fafafa")
subp1 = p.vbar(x="labels", top="only_issues", width=0.9, color="#9A44B6",
               source=data, legend_label="Issues only")
p.vbar(x="labels", top="only_prs", width=0.9, color="#338ADD", fill_alpha=0.75,
       source=data, legend_label="PRs only")
p.vbar(x="labels", top="both_issues_prs", width=0.9, color="lightgreen",
       fill_alpha=0.5, source=data, legend_label="Issues & PRs")

p.add_tools(HoverTool(tooltips=TOOLTIPS, renderers=[subp1]))

p.y_range.start = 0
p.yaxis.axis_label = '# Contributors'
p.x_range.range_padding = 0.1
p.xaxis.major_label_orientation = np.pi / 2
p.xaxis.major_label_text_font_size = "18pt"
p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None
p.legend.click_policy = "hide"
p.legend.location = "top_right"

show(p)
