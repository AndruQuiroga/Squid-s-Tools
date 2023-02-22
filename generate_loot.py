import pickle
from glob import glob

import numpy as np
import pandas as pd

from loot_utils import Money, Inventory, Encounter, LifeStyle


class Loot:

    def __init__(self, Encounter=None, loot_quality=None, num_enemies=None):
        self.encounter = Encounter
        self.loot_quality = loot_quality
        self.loot = [token.inventory for token in self.encounter.tokens]
        self.scale_wealth()
        self.roll_items()

    def scale_wealth(self):
        for l in self.loot:
            if self.loot_quality == 'FAILURE':
                l.money = Money()
            elif self.loot_quality == 'BAD':
                l.money = Money(l.money.get_balance * .50)
            elif self.loot_quality == 'NOT GOOD':
                l.money = Money(l.money.get_balance * .75)
            elif self.loot_quality == 'AVERAGE':
                l.money = Money(l.money.get_balance)
            elif self.loot_quality == 'GOOD':
                l.money = Money(l.money.get_balance * 1.25)
            elif self.loot_quality == 'GREAT':
                l.money = Money(l.money.get_balance * 2.0)

    def roll_items(self):
        if self.loot_quality == 'FAILURE':
            r = LootRoller(item_rate=0.0)
        elif self.loot_quality == 'BAD':
            r = LootRoller(item_rate=.05, sub_common_chance=0.99, common_rate_chance=0.01)
        elif self.loot_quality == 'NOT GOOD':
            r = LootRoller(item_rate=.10, sub_common_chance=0.75, common_rate_chance=0.25)
        elif self.loot_quality == 'AVERAGE':
            r = LootRoller(item_rate=.15, sub_common_chance=0.75, common_rate_chance=0.25)
        elif self.loot_quality == 'GOOD':
            r = LootRoller(item_rate=.20, common_rate_chance=.85, uncommon_rate_chance=.15)
        else:
            r = LootRoller(item_rate=.25, common_rate_chance=.50, uncommon_rate_chance=.50)

        for l in self.loot:
            if np.random.random() < r.item_rate:
                item_type = r.roll_item()
                if item_type:
                    l.items.append(item_type)

    def __str__(self):
        s = ""
        for l in self.loot:
            s += str(l) + '\n'
        return s


ITEM_DATABASE = pd.read_csv('data/Items.csv')


class LootRoller:
    def __init__(self, item_rate=0.0, sub_common_chance=0.0, common_rate_chance=0.0, uncommon_rate_chance=0.0):
        self.item_rate = item_rate
        self.sub_common = sub_common_chance
        self.common_rate = common_rate_chance
        self.uncommon_rate = uncommon_rate_chance

    def roll_item(self):
        roll = np.random.random()
        bins = [self.uncommon_rate,
                self.uncommon_rate + self.common_rate,
                self.uncommon_rate + self.common_rate + self.sub_common]
        x = np.digitize(roll, bins)

        if x == 0:
            return "UNCOMMON_ITEM"
        elif x == 1:
            return "COMMON_ITEM"
        elif x == 2:
            return "MUNDANE_ITEM"

        return ""


if __name__ == '__main__':

    # ask if user wants to load a file
    if input('Load a file? (y/n): ') == 'y':
    # glob all pkl files in the current directory

        files = glob('*.pkl')

        # ask user to select a file
        for i, file in enumerate(files):
            print(f'{i}: {file}')

        file = files[int(input('Select a file: '))]
        # unpickle the file
        with open(file, 'rb') as f:
            Encounter = pickle.load(f)

    else:
        # ask user for how many enemies
        num_enemies = int(input('How many enemies? '))
        # print out the enemy lifestyles
        for i, lifestyle in enumerate(LifeStyle):
            print(f'{i}: {lifestyle}')
        # ask user for enemy lifestyle
        enemy_lifestyle = LifeStyle(int(input('Select a lifestyle: ')))

        Encounter = Encounter(num_minion_tokens=num_enemies,
                              num_boss_tokens=0,
                              enemy_lifestyle=enemy_lifestyle,
                              html=False)

    # ask user what loot quality they want
    loot_quality_dict = {
        (1, 40): 'FAILURE',
        (41, 47): 'BAD',
        (47, 53): 'NOT GOOD',
        (53, 60): 'AVERAGE',
        (60, 67): 'GOOD',
        (67, 100): 'GREAT',
    }
    # ask user for Loot roll
    roll = int(input('Enter The Loot roll: '))
    loot_quality = None
    for k, v in loot_quality_dict.items():
        if k[0] <= roll <= k[1]:
            loot_quality = v
            print(f'Loot Quality: {loot_quality}')
            break

    LootGen = Loot(Encounter, loot_quality=loot_quality)
    print(LootGen)

    input('Press Enter to exit...')

