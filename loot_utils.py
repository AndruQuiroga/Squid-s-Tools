import pickle
import uuid
from enum import Enum
import pandas as pd
import numpy as np


# from html_utils import create_html_stat_block


class Weapon:
    WEAPON_DB = None

    def __init__(self, name, damage, damage_type, weight, value, properties, description):
        self.name = name
        self.damage = damage
        self.damage_type = damage_type
        self.weight = weight
        self.value = value
        self.properties = properties
        self.description = description

    @staticmethod
    def create_weapon_from_row(row):
        properties = row['Properties'].split(',')
        damage = properties[0]
        damage_type = properties[1]
        extra = ''
        if '-' in row['Properties']:
            extra = row['Properties'].split('-')[1]
        return Weapon(row['Name'], damage, damage_type,
                      row['Weight'], row['Value'], extra, row['Text'])

    @classmethod
    def get_all_weapons(cls):
        if cls.WEAPON_DB is None:
            df = pd.read_csv('./data/Items.csv')
            df = df[['weapon' in str(x) for x in df['Type'].to_numpy()]]
            weapons = [Weapon.create_weapon_from_row(row) for index, row in df.iterrows()]

            cls.WEAPON_DB = weapons
        return cls.WEAPON_DB

    def __str__(self):
        return f"{self.name} ({self.damage} {self.damage_type})"


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
MONSTER_DB = pd.read_csv('data/Bestiary.csv')


class Token:

    def __init__(self, encounter=None, token_name='', boss=False, enemey_life_style=None):
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
        self.encounter = encounter
        self.id = str(uuid.uuid4())
        if token_name in MONSTER_DB['Name'].to_numpy():
            self.get_monster_from_database(token_name)

        self.generate_wealth(enemey_life_style)
        self.initiative = self.roll_initiative()


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

    def token_block(self):
        return f"""
        <div class="monster_block dark1 light" onclick="load_token_stat_block('{self.encounter.id}', '{self.id}')">
          <div><span class="monster_name">{self.name}</span>
          <span class="glyphicon glyphicon-trash al-right"></span></div>
          <div class="gradient"></div>

            <div class="light stat_small">
                <div><span class="bold">Armor Class </span><span>{self.ac}</span></div>
                <div><span class="bold">Hit Points </span><span>{self.hit_points}</span></div>
                <div><span class="bold">Speed </span><span>{self.info['Speed'].to_numpy()[0]}</span></div>
                <div><span class="bold">Initiative </span><span>{self.initiative}</span></div>
            </div>
        </div>
        """

    def get_token_stat_block(self):
        return f"""
            <div contenteditable="true"  style="width:310px; font-family:Arial,Helvetica,sans-serif;font-size:11px;">
            
            <div>
            <input class='dark light' id='tname{self.id}' type='text' 
            onchange="change_t_name('{self.encounter.id}', '{self.id}', 'tname{self.id}')" value='{self.name}'></div>
            
            <div class="description">None</div>

            <div class="gradient"></div>

            <div>
                <div ><span class="bold">Armor Class</span><span> {self.info['AC'].to_numpy()[0]}</span></div>
                <div><span class="bold">Hit Points</span><span> 
                
                <input class='dark light' id='thp{self.id}' type='text' 
            onchange="change_t_hp('{self.encounter.id}', '{self.id}', 'thp{self.id}')" value='{self.hit_points}'>
                </span></div>
                
                <div><span class="bold">Speed</span><span> {self.info['Speed'].to_numpy()[0]}</span></div>
            </div>

            <div class="gradient"></div>

            <table>
                <tr><th>STR    </th><th>DEX   </th><th>CON    </th><th>INT   </th><th>WIS   </th><th>CHA   </th></tr>
                <tr><td>{self.info['Strength'].to_numpy()[0]}</td><td>{self.info['Dexterity'].to_numpy()[0]}</td><td>{self.info['Constitution'].to_numpy()[0]}</td>
                <td>{self.info['Intelligence'].to_numpy()[0]}</td><td>{self.info['Wisdom'].to_numpy()[0]}</td><td>{self.info['Charisma'].to_numpy()[0]}</td></tr>
            </table>

            <div class="gradient"></div>

            <div><span class="bold">Senses</span><span>{self.info['Senses'].to_numpy()[0]}</span></div>
            <div><span class="bold">Languages</span><span>{self.info['Languages'].to_numpy()[0]}</span></div>
            <div><span class="bold">Challenge</span><span>{self.cr}</span></div> 

            <div class="gradient"></div>

            <div class="actions">Actions</div>
            <p>{self.info['Actions'].to_numpy()[0]}</p>
            <div class="gradient"></div>

            </div>
            """

    def __str__(self):
        return self.name

    def roll_initiative(self):
        dex_mod = self.info['Dexterity'].to_numpy()[0] // 2 - 5
        return np.random.randint(1, 21) + dex_mod

    def __gt__(self, other):
        return self.initiative > other.initiative

    def __lt__(self, other):
        return self.initiative < other.initiative


class Player(Token):

    def __init__(self, encounter, name):
        self.name = name
        self.encounter = encounter
        self.id = str(uuid.uuid4())
        self.initiative = 0
        pass

    def token_block(self):
        return f"""
        <div class="monster_block dark1 light" onclick="load_token_stat_block('{self.encounter.id}', '{self.id}')">
          <div><span class="monster_name">{self.name}</span>
          <span class="glyphicon glyphicon-trash al-right"></span></div>
          <div class="gradient"></div>

            <div class="light stat_small">
                <div><span class="bold">Initiative </span><span>{self.initiative}</span></div>
            </div>
        </div>
        """

    def get_token_stat_block(self):
        return f"""
            <div contenteditable="true"  style="width:310px; font-family:Arial,Helvetica,sans-serif;font-size:11px;">
            <input class='dark light' id='pname{self.id}' type='text' 
            onchange="change_t_name('{self.encounter.id}', '{self.id}', 'pname{self.id}')" value='{self.name}'></div>
            <div class="description">initiative: <input class='dark light' id='pinit{self.id}' type='number' 
            onchange="change_p_init('{self.encounter.id}', '{self.id}', 'pinit{self.id}')"></div>
            """


class Encounter:

    def __init__(self, token_blueprint,
                 html=True):
        # if cr is None and base_token is not None:
        #     cr = Token(base_token).cr

        # print(cr)
        # self.cr = cr
        # self.environment = None
        # self.base_token = base_token
        # self.life_style = enemy_lifestyle
        self.id = str(uuid.uuid4())
        self.name = "Encounter"
        self.tokens = self.generate_tokens(token_blueprint)
        for i in range(5):
            self.tokens.append(Player(self, f"Player_{i}"))
        self.save()
        # self.loot = []

        # if num_minion_tokens is None:
        #     if cr is not None:
        #         party_cr_rating = ((party_level * num_players) / 4)
        #         num_total_tokens = int(np.ceil(party_cr_rating / cr))
        #     else:
        #         num_total_tokens = num_players * 2
        #
        #     num_minion_tokens = num_total_tokens - num_boss_tokens
        #
        # self.num_boss_tokens = num_boss_tokens
        # self.num_minion_tokens = num_minion_tokens
        #
        # if num_special_weapons is None and np.random.random() > .90:
        #     num_special_weapons = 1

        # if html:
        #     create_html_stat_block(self.tokens)
        # self.generate_loot()

    def sort_tokens(self):
        self.tokens.sort(reverse=True)

    def generate_tokens(self, token_blueprint=None, environment=None):
        if environment is not None:
            return []

        tokens = []
        for token in token_blueprint:
            for i in range(token['boss_count']):
                tokens.append(Token(self, token['name'], boss=True))
            for i in range(token['minion_count']):
                tokens.append(Token(self, token['name']))

        return tokens

    def html_block(self):
        f"""
        <div class="encounter_block">{self.name}</div>
        """

    def save(self):
        with open(f'./saves/{self.name}.encounter', 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)

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
