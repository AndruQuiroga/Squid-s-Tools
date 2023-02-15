import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# random items
# random n weapons
# random 1% uncommon
# random 0.5% rare



# load the data
df = pd.read_csv('Bestiary.csv')
df = df[df['Environment'].notna()]
print(df)
crs_str = df['CR'].to_numpy()
crs = []
for cr in crs_str:
    if type(cr) != str:
        crs.append(100)
        continue
    if cr == 'Unknown':
        crs.append(100)
        continue

    cr = cr.split(' ')[0]
    if '/' in cr:
        num, dom = cr.split('/')
        cr = float(num) / float(dom)
    else:
        cr = float(cr)
    crs.append(cr)

crs = np.array(crs)
df['CR'] = crs
df = df[df['CR'] <= 1]
print(df)

# sort by environment
df = df.sort_values(by=['Environment'])
df.to_csv('Bestiary_filtered.csv', index=False)
print(df)





