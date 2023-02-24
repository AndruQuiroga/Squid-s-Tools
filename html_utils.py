import glob
import eel as eel
import pandas as pd
from loot_utils import Weapon, Encounter


monster_df = pd.read_csv('./data/Bestiary_filtered.csv')
item_df = pd.read_csv('./data/Items.csv')


@eel.expose
def get_monster_list():
    print("Retrieving monster list")
    return [{"id": i, "text": x} for i, x in enumerate(monster_df['Name'])]


@eel.expose
def get_weapon_list():
    print("Retrieving weapon list")
    weapons = Weapon.get_all_weapons()
    return [{"id": i, "text": str(x)} for i, x in enumerate(weapons)]


@eel.expose
def add_monster_to_encounter_builder(js_arr):
    monster_name = js_arr[0]['text']
    monster = monster_df[monster_df['Name'] == monster_name]
    s = "<tr>"
    s += f"<td>{monster['Name'].to_numpy()[0]}</td>"
    s += f"<td><select class=\"weapon-selection\"multiple=\"multiple\"></select></td>"
    s += f"<td><input type='number'></td>"
    s += f"<td><input type='number'></td>"
    s += "<td><input type=\"checkbox\"></td>"
    s += "<td><button type=\"button\" class=\"btn\">Remove</button></td>"
    s += "</tr>"
    return s

@eel.expose
def create_encounter(token_blueprint):
    print(token_blueprint)
    encounter = Encounter(token_blueprint)
    return True

def encounter_selection_block(x):
    return f"""
    <div class="encounter_block" onclick="load_encounter('{x.id}')">
        <div class="encounter-name">{x.name}</div>
        <div class="encounter-description">None</div>
    </div>
    """

Encounter_Object_List = None
def get_all_encounters(reload=False):
    global Encounter_Object_List
    if Encounter_Object_List is None or reload:
        Encounter_Object_List = [Encounter.load(file) for file in glob.glob('./saves/*.encounter')]

    return Encounter_Object_List


@eel.expose
def get_encounter_list():
    return [encounter_selection_block(x) for x in get_all_encounters()]


@eel.expose
def load_encounter(encounter_id):
    # find the encounter in Ecounter_Object_List
    encounter = [x for x in get_all_encounters() if x.id == encounter_id][0]
    encounter_blocks = [token.token_block() for token in encounter.tokens]
    return ''.join(encounter_blocks)


@eel.expose
def load_token_stat_block(encounter_id, token_id):
    # find the encounter in Ecounter_Object_List
    encounter = [x for x in get_all_encounters() if x.id == encounter_id][0]
    print(encounter.tokens)
    print(token_id)
    print([x.id for x in encounter.tokens])
    token     = [x for x in encounter.tokens if x.id == token_id][0]
    return token.get_token_stat_block()
