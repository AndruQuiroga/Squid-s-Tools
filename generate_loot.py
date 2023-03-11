import pickle
from glob import glob

import numpy as np
import pandas as pd

ITEM_DATABASE = pd.read_csv('data/Items_filtered.csv')

common_dict = {
    'scroll': 0.30,
    'potion': 0.55,
    'other_magic': 0.10,
    'other_mundane': 0.05,
}

uncommon_dict = {
        '+1 Weapon': 0.30,
        'Unique Weapon/Armor': 0.02,
        'scroll': 0.22,
        'potion': 0.26,
        'other_magic': 0.17,
        'other_mundane': 0.03,
    }


def preroll_item(item_rarity):
    """
    Generic common items (things found in chests or shops)
    :param num_items:
    :return:
    """

    if item_rarity == 'mundane':
        mundane_items = pd.read_csv('data/mundane_items.csv')
        item = mundane_items.sample(1)
        return item.iloc[0]

    if item_rarity == 'common':

        common_items = ITEM_DATABASE[ITEM_DATABASE['Rarity'] == 'common']
        common_mundane_items = pd.read_csv('data/common_mundane_items.csv')

        # types of common items to choose from are [scroll, potion, other]
        item_type = np.random.choice(list(common_dict.keys()), p=list(common_dict.values()))

        if item_type == 'Scroll':
            item = common_items[common_items['Type'] == 'scroll'].sample(1)
        elif item_type == 'Potion':
            item = common_items[common_items['Type'] == 'potion'].sample(1)
        elif item_type == 'Other_Magic':
            item = common_items[~common_items['Type'].str.contains('potion|scroll')].sample(1)
        else:
            item = common_mundane_items.sample(1)

        return item.iloc[0]

    if item_rarity == 'uncommon':

        common_items = ITEM_DATABASE[ITEM_DATABASE['Rarity'] == 'uncommon']
        common_mundane_items = pd.read_csv('data/uncommon_mundane_items.csv')

        item_type = np.random.choice(list(uncommon_dict.keys()), p=list(uncommon_dict.values()))

        if item_type == '+1 Weapon':
            item = common_items[common_items['Name'] == '+1 Weapon']
        elif item_type == 'Unique Weapon/Armor':
            item = common_items[common_items['Type'].str.contains('generic')].sample(1)
        elif item_type == 'Scroll':
            item = common_items[common_items['Type'] == 'scroll'].sample(1)
        elif item_type == 'Potion':
            item = common_items[common_items['Type'] == 'potion'].sample(1)
        elif item_type == 'Other_Magic':
            item = common_items[~common_items['Type'].str.contains('potion|scroll|generic')].sample(1)
        else:
            item = common_mundane_items.sample(1)

        return item.iloc[0]


# for _ in range(10):
#     item = pick_common_prerolled_items()[0].to_dict()
#     print(f"{item['Name']} {item['Type']} - {item['Value']}")

def create_mundane_datasets():
    mundane_items = ITEM_DATABASE[ITEM_DATABASE['Rarity'] == 'none']
    mundane_items = mundane_items[~mundane_items['Type'].str.contains('vehicle|mount', case=False)]
    mundane_items = mundane_items[mundane_items['Value'].str.contains('gp', case=False, na=False)]
    mundane_items['int_Value'] = mundane_items['Value'].str.replace('gp', '')
    mundane_items['int_Value'] = mundane_items['int_Value'].str.replace(',', '')
    mundane_items['int_Value'] = mundane_items['int_Value'].astype(int)
    mundane_items = mundane_items[mundane_items['int_Value'] < 50]
    mundane_items.drop(columns=['int_Value'], inplace=True)

    for i, item in mundane_items.iterrows():
        print(f"{item['Name']:<30s} {item['Type']:>80s} - {item['Value']:>10s}")

    # to csv
    mundane_items.to_csv('data/mundane_items.csv', index=False)

    mundane_items = ITEM_DATABASE[ITEM_DATABASE['Rarity'] == 'none']
    mundane_items = mundane_items[~mundane_items['Type'].str.contains('vehicle|mount', case=False)]
    mundane_items = mundane_items[mundane_items['Value'].str.contains('gp', case=False, na=False)]
    mundane_items['int_Value'] = mundane_items['Value'].str.replace('gp', '')
    mundane_items['int_Value'] = mundane_items['int_Value'].str.replace(',', '')
    mundane_items['int_Value'] = mundane_items['int_Value'].astype(int)
    mundane_items = mundane_items[mundane_items['int_Value'] <= 100]
    mundane_items = mundane_items[mundane_items['int_Value'] >= 50]
    mundane_items.drop(columns=['int_Value'], inplace=True)

    # to csv
    mundane_items.to_csv('data/common_mundane_items.csv', index=False)

    mundane_items = ITEM_DATABASE[ITEM_DATABASE['Rarity'] == 'none']
    mundane_items = mundane_items[~mundane_items['Type'].str.contains('vehicle|mount|renaissance', case=False)]
    mundane_items = mundane_items[mundane_items['Value'].str.contains('gp', case=False, na=False)]
    mundane_items['int_Value'] = mundane_items['Value'].str.replace('gp', '')
    mundane_items['int_Value'] = mundane_items['int_Value'].str.replace(',', '')
    mundane_items['int_Value'] = mundane_items['int_Value'].astype(int)
    mundane_items = mundane_items[mundane_items['int_Value'] <= 500]
    mundane_items = mundane_items[mundane_items['int_Value'] > 100]
    mundane_items.drop(columns=['int_Value'], inplace=True)

    # to csv
    mundane_items.to_csv('data/uncommon_mundane_items.csv', index=False)

create_mundane_datasets()

# class Loot:
#
#     def __init__(self, Encounter=None, loot_quality=None, num_enemies=None):
#         self.encounter = Encounter
#         self.loot_quality = loot_quality
#         self.loot = [token.inventory for token in self.encounter.tokens if hasattr(token, 'inventory')]
#         self.scale_wealth()
#         self.roll_items()
#
#     def scale_wealth(self):
#         for l in self.loot:
#             if self.loot_quality == 'FAILURE':
#                 l.money = Money()
#             elif self.loot_quality == 'BAD':
#                 l.money = Money(l.money.get_balance * .50)
#             elif self.loot_quality == 'NOT GOOD':
#                 l.money = Money(l.money.get_balance * .75)
#             elif self.loot_quality == 'AVERAGE':
#                 l.money = Money(l.money.get_balance)
#             elif self.loot_quality == 'GOOD':
#                 l.money = Money(l.money.get_balance * 1.25)
#             elif self.loot_quality == 'GREAT':
#                 l.money = Money(l.money.get_balance * 2.0)
#
#     def roll_items(self):
#         if self.loot_quality == 'FAILURE':
#             r = LootRoller(item_rate=0.0)
#         elif self.loot_quality == 'BAD':
#             r = LootRoller(item_rate=.05, sub_common_chance=0.99, common_rate_chance=0.01)
#         elif self.loot_quality == 'NOT GOOD':
#             r = LootRoller(item_rate=.10, sub_common_chance=0.75, common_rate_chance=0.25)
#         elif self.loot_quality == 'AVERAGE':
#             r = LootRoller(item_rate=.15, sub_common_chance=0.75, common_rate_chance=0.25)
#         elif self.loot_quality == 'GOOD':
#             r = LootRoller(item_rate=.20, common_rate_chance=.85, uncommon_rate_chance=.15)
#         else:
#             r = LootRoller(item_rate=.25, common_rate_chance=.50, uncommon_rate_chance=.50)
#
#         for l in self.loot:
#             if np.random.random() < r.item_rate:
#                 item_type = r.roll_item()
#                 if item_type:
#                     l.items.append(item_type)
#
#     def __str__(self):
#         s = ""
#         for l in self.loot:
#             s += str(l) + '\n'
#         return s
#
#
# class LootRoller:
#     def __init__(self, item_rate=0.0, sub_common_chance=0.0, common_rate_chance=0.0, uncommon_rate_chance=0.0):
#         self.item_rate = item_rate
#         self.sub_common = sub_common_chance
#         self.common_rate = common_rate_chance
#         self.uncommon_rate = uncommon_rate_chance
#
#     def roll_item(self):
#         roll = np.random.random()
#         bins = [self.uncommon_rate,
#                 self.uncommon_rate + self.common_rate,
#                 self.uncommon_rate + self.common_rate + self.sub_common]
#         x = np.digitize(roll, bins)
#
#         if x == 0:
#             return "UNCOMMON_ITEM"
#         elif x == 1:
#             return "COMMON_ITEM"
#         elif x == 2:
#             return "MUNDANE_ITEM"
#
#         return ""




# if __name__ == '__main__':
#
#     # ask if user wants to load a file
#     if input('Load a file? (y/n): ') == 'y':
#         # glob all pkl files in the current directory
#
#         files = glob('./saves/*.encounter')
#
#         # ask user to select a file
#         for i, file in enumerate(files):
#             print(f'{i}: {file}')
#
#         file = files[int(input('Select a file: '))]
#         # unpickle the file
#         with open(file, 'rb') as f:
#             Encounter = pickle.load(f)
#
#     else:
#         # ask user for how many enemies
#         num_enemies = int(input('How many enemies? '))
#         # print out the enemy lifestyles
#         for i, lifestyle in enumerate(LifeStyle):
#             print(f'{i}: {lifestyle}')
#         # ask user for enemy lifestyle
#         enemy_lifestyle = LifeStyle(int(input('Select a lifestyle: ')))
#
#         Encounter = Encounter(num_minion_tokens=num_enemies,
#                               num_boss_tokens=0,
#                               enemy_lifestyle=enemy_lifestyle,
#                               html=False)
#
#     # ask user what loot quality they want
#     loot_quality_dict = {
#         (1, 40): 'FAILURE',
#         (41, 47): 'BAD',
#         (47, 53): 'NOT GOOD',
#         (53, 60): 'AVERAGE',
#         (60, 67): 'GOOD',
#         (67, 100): 'GREAT',
#     }
#     # ask user for Loot roll
#     roll = int(input('Enter The Loot roll: '))
#     loot_quality = None
#     for k, v in loot_quality_dict.items():
#         if k[0] <= roll <= k[1]:
#             loot_quality = v
#             print(f'Loot Quality: {loot_quality}')
#             break
#
#     LootGen = Loot(Encounter, loot_quality=loot_quality)
#     print(LootGen)
#
#     input('Press Enter to exit...')
