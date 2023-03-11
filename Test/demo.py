import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from SquidsTools.loot_utils import Money

r1 = np.random.randint(1, 21, 100000)
r2 = np.random.randint(1, 21, 100000)

# get higher of the two
r3 = np.maximum(r1, r2)
plt.hist(r3, bins=20)
plt.show()

loot_rolls = np.random.randint(1, 21, (5, 1000000))
loot_rolls = loot_rolls.sum(axis=0)

plt.hist(loot_rolls, bins=100, range=(1, 100))

center = 52.5
bins = [1,
        center - 13,
        center - 6,
        center,
        center + 6,
        center + 13,
        100]

bins = [1,
        36,
        43,
        51,
        62,
        70,
        100]

for i in range(1, len(bins) - 1):
    plt.axvline(bins[i], ls='--', c='r')
plt.show()

counts, *_ = plt.hist(loot_rolls, bins=bins, range=(1, 100))
counts /= 1000000

labels = {(1, 40): 'FAILURE',
          (41, 47): 'BAD',
          (47, 53): 'NOT GOOD',
          (53, 60): 'AVERAGE',
          (60, 67): 'GOOD',
          (67, 100): 'GREAT'}
labels = list(labels.values())
for i in range(len(bins) - 1):
    print(f"{labels[i]:<10s} {bins[i]:3.0f}-{bins[i + 1]:<3.0f}: {counts[i]:0.0%}")


items_csv = pd.read_csv("../SquidsTools/data/Items.csv")
mundane_items = items_csv[items_csv['Rarity'] == 'none']
mundane_items = mundane_items[~mundane_items['Value'].isna()]

moneies = []
for value in mundane_items['Value']:
    if value == '':
        continue
    moneies.append(Money.money_from_file(value).get_balance)

print(len(moneies), len(mundane_items))
moneies = np.array(moneies)
print(moneies.mean(), moneies.std())
plt.show()
plt.hist(moneies, bins=20, range=(0, 10000))
plt.show()