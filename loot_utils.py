import glob
import pickle
import uuid
from enum import Enum
import pandas as pd
import numpy as np

from generate_loot import preroll_item


# from html_utils import create_html_stat_block

def scan_token_for_weapons(token_actions):
    weapon_names = [w.name for w in Weapon.get_all_weapons()]
    weapon_names = [x.split(' (')[0] for x in weapon_names]
    weapons_found = []
    for i, name in enumerate(weapon_names):
        print(name)
        if name in token_actions:
            weapons_found.append(i)
    print(token_actions)
    return weapons_found


class LifeStyle(Enum):
    """Types of wealth"""
    Wretched = 0
    Squalid = 1
    Poor = 2
    Modest = 3
    Comfortable = 4
    Wealthy = 5
    Aristocratic = 6


class Weapon:
    WEAPON_DB = None

    def __init__(self, name,
                 damage,
                 damage_type,
                 weapon_type,
                 weight,
                 value,
                 rarity,
                 properties,
                 description):

        self.name = name
        self.damage = damage
        self.damage_type = damage_type
        self.weapon_type = weapon_type
        self.weight = weight
        self.value = value
        self.rarity = rarity
        self.properties = properties
        self.description = description
        self.ranged = 'range' in weapon_type

    @staticmethod
    def create_weapon_from_id(id):
        return Weapon.get_all_weapons()[id]

    @staticmethod
    def create_weapon_from_row(row):
        properties = row['Properties'].split(',')
        damage = properties[0]
        damage_type = properties[1]
        properties = []
        if '-' in row['Properties']:
            properties = row['Properties'].split('-')[1][1:]
            properties = properties.split(', ')
        return Weapon(row['Name'], damage, damage_type, row['Type'],
                      row['Weight'], row['Value'], row['Rarity'], properties, row['Text'])

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

    def __init__(self, life_style=None, copper=0):
        self.platinum = 0
        self.gold = 0
        self.silver = 0
        self.copper = copper
        self.balance()

        if life_style is not None:
            self.generate_wealth(life_style)

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

    def generate_wealth(self, wealth_type: LifeStyle):
        if wealth_type == LifeStyle.Wretched:
            days_of_money = 0
        elif wealth_type == LifeStyle.Squalid:
            days_of_money = 1
            daily_income = np.random.randint(6, 12)
            self.copper = daily_income * days_of_money
        elif wealth_type == LifeStyle.Poor:
            days_of_money = np.random.randint(1, 3)
            daily_income = np.random.randint(12, 25)
            self.copper = daily_income * days_of_money
        elif wealth_type == LifeStyle.Modest:
            days_of_money = np.random.randint(3, 6)
            daily_income = np.random.randint(75, 150)
            self.copper = daily_income * days_of_money
        elif wealth_type == LifeStyle.Comfortable:
            days_of_money = np.random.randint(6, 10)
            daily_income = np.random.randint(150, 300)
            self.copper = daily_income * days_of_money
        elif wealth_type == LifeStyle.Wealthy:
            days_of_money = np.random.randint(10, 16)
            daily_income = np.random.randint(300, 600)
            self.copper = daily_income * days_of_money
        elif wealth_type == LifeStyle.Aristocratic:
            days_of_money = np.random.randint(16, 21)
            daily_income = np.random.randint(1000, 1500)
            self.copper = daily_income * days_of_money

        self.balance()

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
        # only print highest valued coin
        if self.platinum > 0:
            return f"{self.platinum}pp"
        elif self.gold > 0:
            return f"{self.gold}gp"
        elif self.silver > 0:
            return f"{self.silver}sp"
        else:
            return f"{self.copper}cp"

    def __repr__(self):
        return f"{self.platinum}pp {self.gold}gp {self.silver}sp {self.copper}cp"


# load monster database
MONSTER_DB = pd.read_csv('data/Bestiary.csv')


class Token:

    def __init__(self,
                 encounter=None,
                 token_name='',
                 boss=False,
                 weapons=None,
                 life_style=None,
                 lootable=True):

        self.encounter = encounter
        self.id = str(uuid.uuid4())
        self.name = token_name
        self.boss = boss
        self.life_style = life_style
        self.lootable = lootable
        self.info = None

        self.hit_points = 0
        self.inventory = Inventory(self, weapons=weapons)

        self.get_monster_from_database(token_name)
        self.set_hit_points()
        self.define_modifiers()
        self.proficiency_bonus = 2
        self.initiative = self.roll_initiative()

    def get_monster_from_database(self, name):
        monster = MONSTER_DB[MONSTER_DB['Name'] == name]
        if len(monster) == 0:
            return None

        self.info = monster.iloc[0].to_dict()

    def define_modifiers(self):
        self.modifiers = {}
        attributes = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        for k, v in self.info.items():
            k = k.lower()
            if k in attributes:
                self.modifiers[k + '_mod'] = int(v) // 2 - 5

    def set_hit_points(self):
        hit_die = self.info['HP']
        hit_die = hit_die.split('(')[1][:-1]
        num_dice = int(hit_die.split('d')[0])
        num_faces = int(hit_die.split('d')[1].split(' ')[0])

        operator = None
        static_mod = None
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
        <div class="monster_block dark1 light {'dead' if self.hit_points <= 0 else 'None'}" id="{self.id}"
        onclick="load_token_stat_block('{self.encounter.id}', '{self.id}')">
          
          <div>
              <span class="token_name">{self.name} {'(DEAD)' if self.hit_points <= 0 else ''}</span>
              <span class="glyphicon glyphicon-trash al-right"></span>
              <span class="	glyphicon glyphicon-screenshot al-right"></span>
          </div>
          
          <div class="gradient"></div>

            <div class="light stat_small">
                <div><span class="bold">Armor Class </span><span>{self.info['AC']}</span></div>
                <div><span class="bold">Hit Points </span><span>{self.hit_points}</span></div>
                <div><span class="bold">Speed </span><span>{self.info['Speed']}</span></div>
                <div><span class="bold">Initiative </span><span>{self.initiative}</span></div>
            </div>
        </div>
        """

    def get_weapon_blocks(self):
        s = ''
        for weapon in self.inventory.weapons:
            to_hit_mod = self.modifiers['strength_mod'] if 'finesse' not in weapon.properties \
                else self.modifiers['dexterity_mod']
            to_hit_mod += self.proficiency_bonus

            damage_mod = self.modifiers['strength_mod'] if 'finesse' not in weapon.properties \
                else self.modifiers['dexterity_mod']

            s += f"""
            <div class="weapon_block dark1 light stat_small">
                <span>{weapon.name}</span>
                <span>Reach: {'5ft' if 'reach' not in weapon.properties else '10ft'}</span>
                <span>To Hit: +{to_hit_mod}</span>
                <span>Damage: {weapon.damage}+{damage_mod} {weapon.damage_type}</span>
            </div>
            """
        return s

    def get_token_stat_block(self):
        return f"""
            <div style="width:310px; font-family:Arial,Helvetica,sans-serif;font-size:11px;">
            
            <div>
            <input class='dark light text-seemless' id='tname{self.id}' type='text' style='font-size:200%;
            font-family:Georgia, serif;font-variant:small-caps;'
            onchange="change_t_name('{self.encounter.id}', '{self.id}', 'tname{self.id}')" value='{self.name}'></div>
            
            <div class="description">{self.info['Type']}, {self.info['Size']}</div>

            <div class="gradient"></div>

            <div>
                <div ><span class="bold">Armor Class</span><span> {self.info['AC']}</span></div>
                <div><span class="bold">Hit Points</span><span> 
                
                <input class='dark light text-seemless' style='width: 30px;' id='thp{self.id}' type='text' 
            onchange="change_t_hp('{self.encounter.id}', '{self.id}', 'thp{self.id}')" value='{self.hit_points}'>
                </span></div>
                
                <div><span class="bold">Speed</span><span> {self.info['Speed']}</span></div>
            </div>

            <div class="gradient"></div>

            <table>
                <tr><th>STR    </th><th>DEX   </th><th>CON    </th><th>INT   </th><th>WIS   </th><th>CHA   </th></tr>
                <tr><td>{self.info['Strength']}</td><td>{self.info['Dexterity']}</td><td>{self.info['Constitution']}</td>
                <td>{self.info['Intelligence']}</td><td>{self.info['Wisdom']}</td><td>{self.info['Charisma']}</td></tr>
            </table>

            <div class="gradient"></div>

            <div><span class="bold">Senses</span><span> {self.info['Senses']}</span></div>
            <div><span class="bold">Languages</span><span> {self.info['Languages']}</span></div>
            <div><span class="bold">Challenge</span><span> {self.info['CR']}</span></div> 

            <div class="gradient"></div>

            <div class="actions">Actions</div>
            <p>{self.info['Actions']}</p>
            <div class="gradient"></div>
            <div class="actions">Weapons</div>
            {self.get_weapon_blocks()}
            <div class="gradient"></div>

            </div>
            """

    def __str__(self):
        return self.name

    def roll_initiative(self):
        dex_mod = self.info['Dexterity'] // 2 - 5
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
        self.lootable = False
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
            <div class="description">initiative: <input class='dark light' id='tinit{self.id}' type='number' 
            onchange="change_t_init('{self.encounter.id}', '{self.id}', 'tinit{self.id}', null)"></div>
            """


class Encounter:

    def __init__(self, token_blueprint, name=None):
        if name is None:
            name = self.generate_name()

        self.id = str(uuid.uuid4())
        self.name = name
        self.tokens = self.generate_tokens(token_blueprint)
        self.save()

    def sort_tokens(self):
        self.tokens.sort(reverse=True)

    def generate_tokens(self, token_blueprint=None, environment=None):
        if environment is not None:
            return []

        tokens = []
        for token in token_blueprint:
            if token['name'] == 'Players':
                for i in range(token['minion_count']):
                    tokens.append(Player(self, f'Player {i + 1}'))
                continue

            for i in range(token['boss_count']):
                tokens.append(Token(self, token['name'], boss=True, weapons=token['weapons']))
            for i in range(token['minion_count']):
                tokens.append(Token(self, token['name'], weapons=token['weapons']))

        return tokens

    def html_block(self):
        f"""
        <div class="encounter_block">{self.name}</div>
        """

    def generate_loot(self):
        s = ''
        lootable_tokens = [token for token in self.tokens if token.lootable]
        # find the lowest square root of the number of tokens
        # this will be the number of columns
        # the number of rows will be the number of tokens divided by the number of columns
        # if the number of tokens is not a perfect square, the last row will have fewer columns
        cols = int(np.sqrt(len(lootable_tokens)))
        rows = len(lootable_tokens) // cols

        for i in range(rows):
            s += '<div class="row">'
            for j in range(cols):
                if i * cols + j < len(lootable_tokens):
                    s += lootable_tokens[i * cols + j].inventory.loot_block()
            s += '</div>'

        return s

    def save(self):
        with open(f'./saves/{self.name}.encounter', 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def generate_name():
        files = glob.glob('./saves/*.encounter')
        if len(files) == 0:
            return "Encounter_1"
        else:
            return f"Encounter_{len(files) + 1}"


"""
    (1, 40): 'FAILURE'   -- Nothing?
    (41, 47): 'BAD'      -- Less Gold / Weapons Broke
    (47, 53): 'NOT GOOD' -- Slightly less gold / Weapons Broke / Cheap Mundane
    (53, 60): 'AVERAGE'  -- What they had / Moderate Mundane
    (60, 67): 'GOOD',    -- Slighty more gold / All Weapons are good/ Good Mundane
    (67, 100): 'GREAT'   -- Uncommon Item (Non-Armor/Weapon) / Decent Mundane

"""

class Inventory:
    def __init__(self, token=None, weapons=None):
        if token is None:
            return

        if not token.lootable:
            return

        print("WEAPONS: ", weapons)

        self.token = token
        self.money = Money(token.life_style)
        self.weapons = [Weapon.create_weapon_from_id(int(weapon)) for weapon in weapons]
        self.armor = []
        self.items = []

        self.generate_loot()

    def generate_loot(self):
        item_spawn_chance = 0.25 if not self.token.boss else 1.00

        if np.random.random() < item_spawn_chance:

            rarity_dict = {
                "mundane":  0.50,
                "common":   0.30,
                "uncommon": 0.20,
            }

            item_rarity = np.random.choice(list(rarity_dict.keys()), p=list(rarity_dict.values()))
            item = preroll_item(item_rarity)
            item = f"({item_rarity}) {item['Name']}"
            self.items.append(item)

        pass

    def loot_block(self):
        print(self.items)
        return f"""
        <div class="loot-block">
        <div style='font-size: 200%;'>{self.token.name}</div>
            Money: {str(self.money):>10}
            Weapons: {', '.join([str(w) for w in self.weapons]):>10}
            Armor: {', '.join([str(w) for w in self.armor]):>10}
            Items: {', '.join([str(w) for w in self.items]):>10}
        </div>
        """

    def __str__(self):
        return f'Name:    {self.token.name}\n' \
               f'Money:   {self.money}\n' \
               f'Weapons: {self.weapons}\n' \
               f'Armor:   {self.armor}\n' \
               f'Items:   {self.items}'
