import os
import pickle
import uuid
import pandas as pd
import numpy as np

from SquidsTools.generate_loot import preroll_item
from enum import Enum


# from html_utils import create_html_stat_block
class Item:

    def __init__(self, name, item_type, rarity, value, weight, description):
        self.name = name
        self.item_type = item_type
        self.value = value
        self.rarity = rarity
        self.weight = weight
        self.description = description
        self.info = None
        self.id = str(uuid.uuid4())


def scan_token_for_weapons(token_actions):
    if isinstance(token_actions, float):
        return []

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
        if self.rarity == 'none':
            self.rarity = 'mundane'
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
            this_dir, this_filename = os.path.split(__file__)
            data_path = os.path.join(this_dir, 'data')
            df = pd.read_csv(os.path.join(data_path, 'Items.csv'))

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
this_dir, this_filename = os.path.split(__file__)
data_path = os.path.join(this_dir, 'data')
MONSTER_DB = pd.read_csv(os.path.join(data_path, 'Bestiary.csv'))


class Token:

    def __init__(self,
                 encounter=None,
                 token_name='',
                 boss=False,
                 weapons=(),
                 life_style=None,
                 lootable=True):

        if token_name == '':
            self.name = 'Container'
            return

        self.encounter = encounter
        self.id = str(uuid.uuid4())
        self.name = token_name
        self.boss = boss
        self.life_style = life_style
        self.lootable = lootable
        self.info = None

        self.hit_points = -1
        self.initiative = -1
        self.inventory = Inventory(self, weapons=weapons)

        if "Item" in self.name:
            return

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
        if len(self.inventory.weapons) == 0:
            return ''

        s = '<div class="actions">Weapons</div>'
        for weapon in self.inventory.weapons:
            if 'finesse' in weapon.properties:
                to_hit_mod = self.modifiers['dexterity_mod']
            elif weapon.ranged:
                to_hit_mod = self.modifiers['dexterity_mod']
            else:
                to_hit_mod = self.modifiers['strength_mod']

            damage_mod = to_hit_mod
            to_hit_mod += self.proficiency_bonus

            if 'reach' in weapon.properties:
                reach = 10
            elif weapon.ranged:
                reach = weapon.properties[0]
            else:
                reach = 5

            s += f"""
            <div class="weapon_block dark1 light">
                <div style="margin: 20px 10px -5px 10px;">
                {weapon.name} ({weapon.rarity})
                </div>
                
                <div class="weapon_stats">
                    Reach: {reach}
                    To Hit: +{to_hit_mod}
                    Damage: {weapon.damage}+{damage_mod} {weapon.damage_type}
                </div>
                
                <div class="weapon_desc">
                    Weight: {weapon.weight}
                    Value: {weapon.value}
                    Description: {weapon.description}
                </div>
            
            </div>
            """
        s += '<div class="gradient"></div>'
        return s

    def get_trait_blocks(self):

        s = '<div class="actions">Traits</div>'
        traits = ['Senses',
                  'Languages',
                  'Skills',
                  'Saving Throws',
                  'Damage Vulnerabilities',
                  'Damage Resistances',
                  'Condition Immunities']
        for trait in traits:
            if isinstance(self.info[trait], float):
                continue
            s += f"<div><span class='bold'>{trait}</span><span> {self.info[trait]}</span></div>"
        if s == '<div class="actions">Traits</div>':
            return ''
        s += '<div class="gradient"></div>'
        return s

    def get_item_blocks(self):
        if len(self.inventory.items) == 0:
            return ''

        s = '<div class="actions">Items</div>'
        for item in self.inventory.items:
            s += f"""
            <div class="item_block dark1 light">
                <div style="font-size: 125%">
                <span>{item.name} ({item.rarity})</span>
                <span class='glyphicon glyphicon-refresh al-right' 
                onclick="replace_item('{self.encounter.id}', '{self.id}', '{item.id}')"></span>
                </div>
                <div class="item_desc">
                    Type: {item.item_type}
                    Weight: {item.weight}
                    Value: {item.value}
                    Description: {item.description}
                </div>
            </div>
            """
        s += '<div class="gradient"></div>'
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
                <tr><td>{self.info['Strength']:2.0f}</td><td>{self.info['Dexterity']:2.0f}</td><td>{self.info['Constitution']:2.0f}</td>
                <td>{self.info['Intelligence']:2.0f}</td><td>{self.info['Wisdom']:2.0f}</td><td>{self.info['Charisma']:2.0f}</td></tr>
            </table>
            <div class="gradient"></div>
            
            {self.get_trait_blocks()}

            <div class="actions">Actions</div>
            <p>{self.info['Actions']}</p>
            <div class="gradient"></div>
            
            {self.get_weapon_blocks()}
            
            {self.get_item_blocks()}

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


class ItemToken(Token):

    def __init__(self,
                 encounter=None,
                 token_name='',
                 boss=False,
                 weapons=(),
                 life_style=None,
                 lootable=True):

        self.encounter = encounter
        self.id = str(uuid.uuid4())
        self.name = token_name
        self.boss = boss
        self.life_style = life_style
        self.lootable = lootable
        self.info = None
        self.initiative = -1

        if "Mundane" in self.name:
            self.inventory = Inventory.preroll('mundane')
        elif "Common" in self.name:
            self.inventory = Inventory.preroll('common')
        elif "Uncommon" in self.name:
            self.inventory = Inventory.preroll('uncommon')
        else:
            self.inventory = Inventory.preroll()
            self.name += f" ({self.inventory.items[0].rarity})"

    def token_block(self):
        return f"""
        <div class="monster_block dark1 light" id="{self.id}"
        onclick="load_token_stat_block('{self.encounter.id}', '{self.id}')">

          <div>
              <span class="token_name">{self.name}</span>
              <span class="glyphicon glyphicon-trash al-right"></span>
          </div>

          <div class="gradient"></div>
        </div>
        """

    def get_token_stat_block(self):
        return f"""
            <div style="width:310px; font-family:Arial,Helvetica,sans-serif;font-size:11px;">

            <div>
            <input class='dark light text-seemless' id='tname{self.id}' type='text' style='font-size:200%;
            font-family:Georgia, serif;font-variant:small-caps; width: 100%;'
            onchange="change_t_name('{self.encounter.id}', '{self.id}', 'tname{self.id}')" value='{self.name}'></div>

            {self.get_weapon_blocks()}

            {self.get_item_blocks()}

            </div>
            """


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
          <div><span class="token_name">{self.name}</span>
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
            name = "Encounter"

        name = self.check_name_uniqueness(name)

        self.id = str(uuid.uuid4())
        self.name = name
        self.tokens = self.generate_tokens(token_blueprint)
        self.save()

    def sort_tokens(self):
        self.tokens.sort(reverse=True)

    def add_tokens(self, token_blueprint=None):
        self.tokens += self.generate_tokens(token_blueprint)
        self.save()

    def generate_tokens(self, token_blueprint=None, environment=None):
        if environment is not None:
            return []

        tokens = []
        for token in token_blueprint:
            if token['name'] == 'Players':
                for i in range(token['minion_count']):
                    tokens.append(Player(self, f'Player {i + 1}'))
                continue

            if token['name'] == 'TOKEN':
                for i in range(token['minion_count']):
                    tokens.append(Player(self, f'TOKEN {i + 1}'))
                continue

            if 'Item' in token['name'] or token['name'] == 'Lootable Container':
                for i in range(token['minion_count']):
                    tokens.append(ItemToken(self, f"{token['name']}"))
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
        # loot_roll = int(loot_roll)
        # num_lootable = int(num_lootable)

        s = ''
        lootable = [token.inventory for token in self.tokens if token.lootable]

        for i in range(len(lootable)):
            s += '<div>'
            s += lootable[i].loot_block()
            s += '</div>'

        return s

    def save(self):
        this_dir, this_filename = os.path.split(__file__)
        save_path = os.path.join(this_dir, 'saves')
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        file_path = os.path.join(save_path, f'{self.name}.encounter')
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    def delete(self):
        this_dir, this_filename = os.path.split(__file__)
        save_path = os.path.join(this_dir, 'saves')
        file_path = os.path.join(save_path, f'{self.name}.encounter')
        os.remove(file_path)

    @staticmethod
    def load(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def check_name_uniqueness(name):
        # if name exists, add a number to the end
        this_dir, this_filename = os.path.split(__file__)
        save_path = os.path.join(this_dir, 'saves')
        if os.path.exists(os.path.join(save_path, f'{name}.encounter')):
            i = 1
            while os.path.exists(os.path.join(save_path, f'{name} ({i}).encounter')):
                i += 1
            name = f'{name} ({i})'
        return name



"""
    (1, 40): 'FAILURE'   -- Nothing?
    (41, 47): 'BAD'      -- Less Gold / Weapons Broke
    (47, 53): 'NOT GOOD' -- Slightly less gold / Weapons Broke / Cheap Mundane
    (53, 60): 'AVERAGE'  -- What they had / Moderate Mundane
    (60, 67): 'GOOD',    -- Slighty more gold / All Weapons are good/ Good Mundane
    (67, 100): 'GREAT'   -- Uncommon Item (Non-Armor/Weapon) / Decent Mundane

"""

class Inventory:
    def __init__(self, token=None, weapons=()):
        if token is None:
            self.token = Token()
            self.money = Money()
            self.weapons = []
            self.armor = []
            self.items = []
            return

        if not token.lootable:
            self.token = token
            self.money = Money()
            self.weapons = []
            self.armor = []
            self.items = []
            return

        print("WEAPONS: ", weapons)

        self.token = token
        self.money = Money(token.life_style)
        self.weapons = [Weapon.create_weapon_from_id(int(weapon)) for weapon in weapons]
        self.armor = []
        self.items = []

        self.generate_loot()

    def generate_loot(self, item_rarity=None, item_spawn_chance=None):
        if item_spawn_chance is None:
            item_spawn_chance = 0.20 if not self.token.boss else 1.00

        if np.random.random() < item_spawn_chance:

            rarity_dict = {
                "mundane":  0.70,
                "common":   0.25,
                "uncommon": 0.05,
            }

            if item_rarity is None:
                item_rarity = np.random.choice(list(rarity_dict.keys()), p=list(rarity_dict.values()))

            item = preroll_item(item_rarity)
            item = Item(item['Name'], item['Type'], item_rarity, item['Value'], item['Weight'], item['Text'])

            # item = f"({item_rarity}) {item['Name']}"
            self.items.append(item)

            if self.token:
                self.token.name = f"{self.token.name} ({item_rarity})"

        pass

    def replace_item(self, old_item):
        item_rarity = old_item.rarity
        item = preroll_item(item_rarity)
        new_item = Item(item['Name'], item['Type'], item_rarity, item['Value'], item['Weight'], item['Text'])

        print("REPLACING ITEM: ", old_item, new_item)
        index = self.items.index(old_item)
        self.items[index] = new_item

    @staticmethod
    def preroll(rarity=None):
        tmp = Inventory()
        tmp.generate_loot(item_rarity=rarity, item_spawn_chance=1.00)
        return tmp

    def loot_block(self):
        print(self.items)

        money = str(self.money)
        weapons = ', '.join([str(w) for w in self.weapons])
        armor = ', '.join([str(w) for w in self.armor])
        items = ', '.join([w.name for w in self.items])

        if money != '0cp':
            money = f'<div> Money: {money:>10} </div>'
        else:
            money = ''

        if weapons != '':
            weapons = f'<div> Weapons: {weapons} </div>'
        if armor != '':
            armor = f'<div> Armor: {armor} </div>'
        if items != '':
            items = f'<div> Items: {items} </div>'

        return f"""
        <div class="loot-block">
        <div style='font-size: 200%;'>{self.token.name}</div>
        {money}
        {weapons}
        {armor}
        {items}
        </div>
        """

    def __str__(self):
        return f'Name:    {self.token.name}\n' \
               f'Money:   {self.money}\n' \
               f'Weapons: {self.weapons}\n' \
               f'Armor:   {self.armor}\n' \
               f'Items:   {self.items}'
