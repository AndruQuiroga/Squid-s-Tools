from enum import Enum
import pandas as pd
import numpy as np

from html_utils import create_html_stat_block


class Money:

    def __init__(self, copper=0):
        self.platinum = 0
        self.gold = 0
        self.silver = 0
        self.copper = copper
        self.balance()

    @staticmethod
    def money_from_file(x):
        m = Money()
        print(x)
        x = x.split(' ')
        if len(x) != 2:
            return m
        num = x[0]
        num = float(num.replace(',', ''))
        m.gold = int(num)
        m.balance()
        return m

    def balance(self):
        bal = self.platinum * 1000 + self.gold * 100 + self.silver * 10 + self.copper
        self.platinum = bal // 1000
        self.gold = (bal % 1000) // 100
        self.silver = (bal % 100) // 10
        self.copper = bal % 10

    def __add__(self, other):
        self.platinum += other.platinum
        self.gold += other.gold
        self.silver += other.silver
        self.copper += other.copper
        self.balance()
        return self

    def __iadd__(self, other):
        self.platinum += other.platinum
        self.gold += other.gold
        self.silver += other.silver
        self.copper += other.copper
        self.balance()
        return self

    @property
    def get_balance(self):
        return self.platinum * 1000 + self.gold * 100 + self.silver * 10 + self.copper

    def __str__(self):
        return f"{self.platinum}pp {self.gold}gp {self.silver}sp {self.copper}cp"

    def __repr__(self):
        return f"{self.platinum}pp {self.gold}gp {self.silver}sp {self.copper}cp"

class LifeStyle(Enum):
    """Types of wealth"""
    Wretched = 0
    Squalid = 1
    Poor = 2
    Modest = 3
    Comfortable = 4
    Wealthy = 5
    Aristocratic = 6

# load monster database
MONSTER_DB = pd.read_csv('Bestiary_filtered.csv')

class Token:

    def __init__(self, token_name, boss=False, enemey_life_style=None):
        self.name = token_name
        self.pouch = Money()
        self.boss = boss
        self.weight = None
        self.size = None
        self.ac = None
        self.cr = None
        self.description = ''
        self.hit_points = 0
        self.inventory = Inventory(self)

        if token_name in MONSTER_DB['Name'].to_numpy():
            self.get_monster_from_database(token_name)

        self.generate_wealth(enemey_life_style)

    def generate_wealth(self, wealth_type: LifeStyle):
        if wealth_type == LifeStyle.Wretched:
            days_of_money = 0
        elif wealth_type == LifeStyle.Squalid:
            days_of_money = 1
            daily_income = np.random.randint(6, 12)
            self.pouch.copper = daily_income * days_of_money
        elif wealth_type == LifeStyle.Poor:
            days_of_money = np.random.randint(1, 3)
            daily_income = np.random.randint(12, 25)
            self.pouch.copper = daily_income * days_of_money
        elif wealth_type == LifeStyle.Modest:
            days_of_money = np.random.randint(3, 6)
            daily_income = np.random.randint(75, 150)
            self.pouch.copper = daily_income * days_of_money
        elif wealth_type == LifeStyle.Comfortable:
            days_of_money = np.random.randint(6, 10)
            daily_income = np.random.randint(150, 300)
            self.pouch.copper = daily_income * days_of_money
        elif wealth_type == LifeStyle.Wealthy:
            days_of_money = np.random.randint(10, 16)
            daily_income = np.random.randint(300, 600)
            self.pouch.copper = daily_income * days_of_money
        elif wealth_type == LifeStyle.Aristocratic:
            days_of_money = np.random.randint(16, 21)
            daily_income = np.random.randint(1000, 1500)
            self.pouch.copper = daily_income * days_of_money

        self.pouch.balance()

    def get_monster_from_database(self, name):
        monster = MONSTER_DB[MONSTER_DB['Name'] == name]
        if len(monster) == 0:
            return None

        self.size = monster['Size'].to_numpy()[0]
        self.cr = monster['CR'].to_numpy()[0]
        self.ac = monster['AC'].to_numpy()[0]
        self.actions = monster['Actions'].to_numpy()[0]
        self.info = monster

        hit_die = monster['HP'].to_numpy()[0]
        hit_die = hit_die.split('(')[1][:-1]
        num_dice = int(hit_die.split('d')[0])
        num_faces = int(hit_die.split('d')[1].split(' ')[0])

        operator = None
        if len(hit_die.split(' ')) > 1:
            operator = hit_die.split(' ')[1]
            static_mod = hit_die.split(' ')[2]

        if self.boss:
            num_dice += 1
        hit_points = np.random.randint(1, num_faces, num_dice).sum()

        if operator == '+':
            hit_points += int(static_mod)
        elif operator == '-':
            hit_points -= int(static_mod)

        self.hit_points = hit_points

    def __str__(self):
        return self.name


class Encounter:

    def __init__(self,
                 cr=None,
                 environment=None,
                 base_token=None,
                 num_boss_tokens=1,
                 num_minion_tokens=None,
                 enemy_lifestyle=LifeStyle.Poor,
                 num_special_weapons=None,
                 num_players=5,
                 party_level=1,
                 html=True):

        if cr is None and base_token is not None:
            cr = Token(base_token).cr

        print(cr)
        self.cr = cr
        self.environment = None
        self.base_token = base_token
        self.life_style = enemy_lifestyle
        self.tokens = []
        self.loot = []

        if num_minion_tokens is None:
            if cr is not None:
                party_cr_rating = ((party_level * num_players) / 4)
                num_total_tokens = int(np.ceil(party_cr_rating / cr))
            else:
                num_total_tokens = num_players * 2

            num_minion_tokens = num_total_tokens - num_boss_tokens

        self.num_boss_tokens = num_boss_tokens
        self.num_minion_tokens = num_minion_tokens

        if num_special_weapons is None and np.random.random() > .90:
            num_special_weapons = 1

        self.generate_tokens()
        if html:
            create_html_stat_block(self.tokens)
        # self.generate_loot()

    def generate_tokens(self):
        if self.environment is not None:
            # pick something
            pass

        if self.base_token is None:
            for i in range(self.num_boss_tokens):
                token = Token(f'Enemy Boss {i + 1}', boss=True, enemey_life_style=self.life_style)
                self.tokens.append(token)
            for i in range(self.num_minion_tokens):
                token = Token(f'Enemy Minion {i + 1}', enemey_life_style=self.life_style)
                self.tokens.append(token)
            return

        for _ in range(self.num_boss_tokens):
            token = Token(self.base_token, boss=True, enemey_life_style=self.life_style)
            self.tokens.append(token)

        for _ in range(self.num_minion_tokens):
            token = Token(self.base_token, enemey_life_style=self.life_style)
            self.tokens.append(token)



"""
    (1, 40): 'FAILURE'   -- Nothing?
    (41, 47): 'BAD'      -- Less Gold / Weapons Broke
    (47, 53): 'NOT GOOD' -- Slightly less gold / Weapons Broke / Cheap Mundane
    (53, 60): 'AVERAGE'  -- What they had / Moderate Mundane
    (60, 67): 'GOOD',    -- Slighty more gold / All Weapons are good/ Good Mundane
    (67, 100): 'GREAT'   -- Uncommon Item (Non-Armor/Weapon) / Decent Mundane

"""
class Inventory:
    def __init__(self, token=None):
        if token is None:
            return
        self.token = token
        self.money = token.pouch
        self.weapons = []
        self.armor = []
        self.items = []

    def __str__(self):
        return f'Name:    {self.token.name}\n' \
               f'Money:   {self.money}\n' \
               f'Weapons: {self.weapons}\n' \
               f'Armor:   {self.armor}\n' \
               f'Items:   {self.items}'

