import numpy as np
from astropy.table import Table
import pylab as pl

tbl = Table.read('astropy_issue_states.txt', format='ascii.fixed_width')
lifetime = np.array([x.strip(" seconds") for x in tbl['Lifetime']]).astype('float')
is_pr = tbl['Is_PR'] == 'True'

pl.figure(1).clf()
pl.hist(lifetime/86400, bins=np.logspace(1-5,8.25-5))
pl.hist(lifetime[is_pr]/86400, bins=np.logspace(1-5,8.25-5))

pl.xscale('log')


pl.figure(2).clf()
pl.hist(lifetime/3600, bins=np.linspace(1,48))
pl.hist(lifetime[is_pr]/3600, bins=np.linspace(1,48))

