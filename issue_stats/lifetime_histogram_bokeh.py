import numpy as np
from astropy.io import ascii
from astropy.table import Table

from bokeh.layouts import column, row
from bokeh.models import RangeSlider, CustomJS
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

lifetime = tbl['Lifetime']
life_days = lifetime / 86400
max_life_days = max(life_days)
logdaybins = np.logspace(-4, 3.25)

# Flags
is_pr = tbl['Is_PR']
is_closed = tbl['State'] == 'closed'

p = figure(title='Lifetime histograms', background_fill_color="#fafafa")
p2 = figure(background_fill_color="#fafafa")

# NOT USED: Closed everything
# hist_closed_total, edges_closed_total = np.histogram(
#    life_days[is_closed], density=False, bins=logdaybins)
# hist1 = p.quad(top=hist_closed_total, bottom=0,
#               left=edges_closed_total[:-1], right=edges_closed_total[1:],
#               fill_color='#A60628', line_color="white",
#               legend_label="Closed (All)")

# Closed Issues
hist_closed_issues, edges_closed_issues = np.histogram(
    life_days[np.logical_and(is_closed, ~is_pr)], density=False,
    bins=logdaybins)
p.quad(top=hist_closed_issues, bottom=0,
       left=edges_closed_issues[:-1], right=edges_closed_issues[1:],
       fill_color="#9A44B6", line_color="white",
       legend_label="Closed Issues")

# Closed PRs
hist_closed_prs, edges_closed_prs = np.histogram(
    life_days[np.logical_and(is_closed, is_pr)], density=False,
    bins=logdaybins)
p.quad(top=hist_closed_prs, bottom=0,
       left=edges_closed_prs[:-1], right=edges_closed_prs[1:],
       fill_color="#338ADD", line_color="white", fill_alpha=0.5,
       legend_label="Closed PRs")

# Open Issues
hist_open_issues, edges_open_issues = np.histogram(
    life_days[np.logical_and(~is_closed, ~is_pr)], density=False,
    bins=logdaybins)
p2.quad(top=hist_open_issues, bottom=0,
        left=edges_open_issues[:-1], right=edges_open_issues[1:],
        fill_color="#9A44B6", line_color="white",
        legend_label="Open Issues")

# Open PRs
hist_open_prs, edges_open_prs = np.histogram(
    life_days[np.logical_and(~is_closed, is_pr)], density=False,
    bins=logdaybins)
p2.quad(top=hist_open_prs, bottom=0,
        left=edges_open_prs[:-1], right=edges_open_prs[1:],
        fill_color="#338ADD", line_color="white", fill_alpha=0.5,
        legend_label="Open PRs")

p.y_range.start = 0
p2.y_range.start = 0

p2.x_range = p.x_range

p.xaxis.axis_label = 'Lifetime (day)'
p.yaxis.axis_label = '#'
p.grid.grid_line_color = "white"
p2.grid.grid_line_color = "white"

# NOTE: Disabled because it messes with slider.
# p.legend.click_policy = "hide"
# p2.legend.click_policy = "hide"

p.add_layout(p.legend[0], 'above')
p2.add_layout(p2.legend[0], 'above')

# Slider
range_callback = CustomJS(args=dict(p=p), code="""
    var a = cb_obj.value;
    p.x_range.start = a[0];
    p.x_range.end = a[1];
""")

range_slider = RangeSlider(
    start=0, end=edges_closed_issues[-1], value=(0, edges_closed_issues[-1]),
    step=1, title='Lifetime range (day)')
range_slider.js_on_change('value', range_callback)

show(column(row(p, p2), range_slider))
