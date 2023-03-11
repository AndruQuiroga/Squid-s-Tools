import glob
import eel as eel
import pandas as pd
from loot_utils import Weapon, Encounter, scan_token_for_weapons, Inventory

monster_df = pd.read_csv('./data/Bestiary.csv')
item_df = pd.read_csv('./data/Items.csv')


@eel.expose
def clear_encounter_builder():
    return f"""
    <form class="formContainer">

            <div>
                <span>Monster Name: </span>
                <span>
                    <select class="monster-selection">
                        <option value="">Select a Monster..</option>
                    </select>
                </span>
                <span>
                    <button type="button" class="btn" onclick="addSelection()">Add</button>
                </span>
            </div>

            <!--  List Selected Monsters -->
            <div class="stat_small">
                <table id="Encounter-Builder-Table">

                    <colgroup>
                        <col span="1" style="width: 30%;">
                        <col span="1" style="width: 50%;">
                        <col span="1" style="width: 10%;">
                        <col span="1" style="width: 10%;">
                        <col span="1" style="width: 10%;">
                    </colgroup>

                    <tbody>
                    <tr>
                        <th>Creature Name</th>
                        <th>Weapons</th>
                        <th># Tokens</th>
                        <th># Bosses</th>
                        <th>Generate Loot? (Items)</th>
                        <th></th>
                    </tr>

                    <tr>
                        <td>Players</td>
                        <td></td>
                        <td><input type='number' value=5></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>

                    </tbody>

                </table>
            </div>
            <div>
                <button type="button" class="btn cancel" onclick="closeForm()">Cancel</button>
                <button type="button" class="btn cancel" onclick="sendForm()">Create</button>
            </div>


        </form>
    """

@eel.expose
def clear_loot_builder():
    return f"""
    <form class="formContainer">

            <div>
                <span>Lootable Containers: </span>
                <span>
                    <input class='dark light text-seemless' id='num_lootable' type='number' value=0>
                </span>
            </div>
            
            <div>
                <span>Player Loot Roll:</span>
                <span>
                    <input class='dark light text-seemless' id='loot_roll_number' type='number' value=0>
                </span>
            </div>

            
            <div>
                <button type="button" class="btn cancel" onclick="closeLootForm()">Cancel</button>
                <button type="button" class="btn cancel" onclick="sendLootForm()">Create</button>
            </div>


        </form>
    """


@eel.expose
def clear_shop_builder():
    return f"""
    <form class="formContainer">

            <div>
                <span>Number Mundane: </span>
                <span>
                    <input class='dark light text-seemless' id='num_mundane' type='number' value=0>
                </span>
            </div>
            
            <div>
                <span>Number Common: </span>
                <span>
                    <input class='dark light text-seemless' id='num_common' type='number' value=0>
                </span>
            </div>
            
            <div>
                <span>Number Uncommon: </span>
                <span>
                    <input class='dark light text-seemless' id='num_uncommon' type='number' value=0>
                </span>
            </div>


            <div>
                <button type="button" class="btn cancel" onclick="closeShopForm()">Cancel</button>
                <button type="button" class="btn cancel" onclick="sendShopForm()">Create</button>
            </div>


        </form>
    """

@eel.expose
def create_shop_inventory(n_mundane, n_common, n_uncommon):
    global loot_table
    containers = []
    for i in range(int(n_mundane)):
        containers.append(Inventory.preroll(rarity='mundane'))
    for i in range(int(n_common)):
        containers.append(Inventory.preroll(rarity='common'))
    for i in range(int(n_uncommon)):
        containers.append(Inventory.preroll(rarity='uncommon'))

    loot_table = ''.join([x.loot_block() for x in containers])
    eel.start('loot.html', port=8001)




@eel.expose
def get_monster_list():
    print("Retrieving monster list")
    return [{"id": i, "text": x} for i, x in enumerate(monster_df['Name'])]


@eel.expose
def get_weapon_list(selected_weapons=()):
    print("Retrieving weapon list")
    weapons = Weapon.get_all_weapons()
    return [{"id": i, "text": str(x), "selected": False if i not in selected_weapons else True}
            for i, x in enumerate(weapons)]


@eel.expose
def add_monster_to_encounter_builder(js_arr):
    print(js_arr)
    token_name = js_arr[0]['text']
    token = monster_df[monster_df['Name'] == token_name].iloc[0]
    token_weapons = scan_token_for_weapons(token['Actions'])
    s = "<tr>"
    s += f"<td>{token_name}</td>"
    s += f"<td><select class=\"weapon-selection\"multiple=\"multiple\"></select></td>"
    s += f"<td><input type='number' value=0></td>"
    s += f"<td><input type='number' value=0></td>"
    s += "<td><input type=\"checkbox\"></td>"
    s += "<td><button type=\"button\" class=\"remove_btn\"'>Remove</button></td>"
    s += "</tr>"
    return s, get_weapon_list(token_weapons)

loot_table = None

@eel.expose
def get_loot_table():
    if loot_table is None:
        return "No Encounter Loaded"
    return loot_table

@eel.expose
def create_loot_table(loot_roll, num_lootable):
    global loot_table
    if Current_Encounter is None:
        return "No Encounter Loaded"
    loot_table = Current_Encounter.generate_loot(loot_roll, num_lootable)
    eel.start('loot.html', port=8001)

@eel.expose
def create_encounter(token_blueprint):
    print("Creating Encounter")
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
Current_Encounter = None

@eel.expose
def get_cuurent_encounter():
    return Current_Encounter

def get_all_encounters(reload=False):
    global Encounter_Object_List
    if Encounter_Object_List is None or reload:
        Encounter_Object_List = [Encounter.load(file) for file in glob.glob('./saves/*.encounter')]

    return Encounter_Object_List


@eel.expose
def get_encounter_list():
    return [encounter_selection_block(x) for x in get_all_encounters(reload=True)]


@eel.expose
def load_encounter(encounter_id):
    global Current_Encounter
    # find the encounter in Ecounter_Object_List
    encounter = [x for x in get_all_encounters() if x.id == encounter_id][0]
    Current_Encounter = encounter
    encounter.sort_tokens()
    buttons = ["""
    <div class='button_wrap'>
    <button class="button" onclick="open_add_token_form()"><strong>Add Token</strong></button>
    <button class="button" onclick="openLootForm()"><strong>Loot Table</strong></button>
    </div>
    """]
    encounter_blocks = [token.token_block() for token in encounter.tokens]
    all = buttons + encounter_blocks
    return ''.join(all)


@eel.expose
def load_token_stat_block(encounter_id, token_id):
    # find the encounter in Ecounter_Object_List
    encounter = [x for x in get_all_encounters() if x.id == encounter_id][0]
    print(encounter.tokens)
    print(token_id)
    print([x.id for x in encounter.tokens])
    token = [x for x in encounter.tokens if x.id == token_id][0]
    return token.get_token_stat_block()


@eel.expose
def change_t_init(encounter_id, token_id, value):
    # find the encounter in Ecounter_Object_List
    print(encounter_id, token_id, value)
    encounter = [x for x in get_all_encounters() if x.id == encounter_id][0]
    print([x.id for x in encounter.tokens])
    print("Token Change Init!!")
    token = [x for x in encounter.tokens if x.id == token_id][0]
    print(value)
    token.initiative = int(value)
    encounter.save()

@eel.expose
def change_t_name(encounter_id, token_id, value):
    # find the encounter in Ecounter_Object_List
    encounter = [x for x in get_all_encounters() if x.id == encounter_id][0]
    print([x.id for x in encounter.tokens])
    print("Token Change Init!!")
    token = [x for x in encounter.tokens if x.id == token_id][0]
    token.name = value
    encounter.save()

@eel.expose
def change_t_hp(encounter_id, token_id, value):
    # find the encounter in Ecounter_Object_List
    encounter = [x for x in get_all_encounters() if x.id == encounter_id][0]
    token = [x for x in encounter.tokens if x.id == token_id][0]
    token.hit_points = int(value)
    encounter.save()

@eel.expose
def replace_item(encounter_id, token_id, item_id):
    encounter = [x for x in get_all_encounters() if x.id == encounter_id][0]
    token = [x for x in encounter.tokens if x.id == token_id][0]
    item = [x for x in token.inventory.items if x.id == item_id][0]
    token.inventory.replace_item(item)
    encounter.save()

@eel.expose
def delete_token(encounter_id, token_id):
    encounter = [x for x in get_all_encounters() if x.id == encounter_id][0]
    token = [x for x in encounter.tokens if x.id == token_id][0]
    encounter.tokens.remove(token)
    encounter.save()
