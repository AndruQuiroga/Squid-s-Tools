import glob
import os
import eel as eel
import pandas as pd
from SquidsTools.loot_utils import Weapon, Encounter, scan_token_for_weapons

this_dir, this_filename = os.path.split(__file__)
data_path = os.path.join(this_dir, 'data')

monster_df = pd.read_csv(os.path.join(data_path, 'Bestiary.csv'))
item_df = pd.read_csv(os.path.join(data_path, 'Items.csv'))


@eel.expose
def clear_encounter_builder():
    return f"""
    <form class="formContainer">

            <div>
                <span>Monster Name: </span>
                <span>
                    <select class="monster-selection" id="builder-monster-selection">
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
def clear_add_token_builder():
    return f"""
    <form class="formContainer">

            <div>
                <span>Monster Name: </span>
                <span>
                    <select class="monster-selection" id='add-monster-selection'>
                        <option value="">Select a Monster..</option>
                    </select>
                </span>
                <span>
                    <button type="button" class="btn" onclick="addTokenSelection()">Add</button>
                </span>
            </div>

            <!--  List Selected Monsters -->
            <div class="stat_small">
                <table id="Encounter-Add-Table">

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
                        <td>TOKEN</td>
                        <td></td>
                        <td><input type='number' value=0></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>

                    </tbody>

                </table>
            </div>
            <div>
                <button type="button" class="btn cancel" onclick="closeTokenForm()">Cancel</button>
                <button type="button" class="btn cancel" onclick="sendTokenForm()">ADD</button>
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
                <span>Number Common Spells: </span>
                <span>
                    <input class='dark light text-seemless' id='num_scommon' type='number' value=0>
                </span>
            </div>
            
            <div>
                <span>Number Uncommon Spells: </span>
                <span>
                    <input class='dark light text-seemless' id='num_suncommon' type='number' value=0>
                </span>
            </div>
            
            <div>
                <span>Number Common Potions: </span>
                <span>
                    <input class='dark light text-seemless' id='num_pcommon' type='number' value=0>
                </span>
            </div>
            
            <div>
                <span>Number Uncommon Potions: </span>
                <span>
                    <input class='dark light text-seemless' id='num_puncommon' type='number' value=0>
                </span>
            </div>


            <div>
                <button type="button" class="btn cancel" onclick="closeShopForm()">Cancel</button>
                <button type="button" class="btn cancel" onclick="sendShopForm()">Create</button>
            </div>


        </form>
    """


@eel.expose
def create_shop_inventory(n_mundane, n_common, n_uncommon, n_scommon, n_suncommon, n_pcommon, n_puncommon):
    global loot_table
    containers = []
    containers.append({"name": "Mundane Item", "minion_count": int(n_mundane)})
    containers.append({"name": "Common Item", "minion_count": int(n_common)})
    containers.append({"name": "Uncommon Item", "minion_count": int(n_uncommon)})
    containers.append({"name": "Common Scroll", "minion_count": int(n_scommon)})
    containers.append({"name": "Uncommon Scroll", "minion_count": int(n_suncommon)})
    containers.append({"name": "Common Potion", "minion_count": int(n_pcommon)})
    containers.append({"name": "Uncommon Potion", "minion_count": int(n_puncommon)})

    encounter = Encounter(containers, name="Shop")
    print("CREATED SHOP ENCOUNTER")


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
    s += "<td><input type=\"checkbox\" checked></td>"
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
def create_loot_table():
    global loot_table
    if Current_Encounter is None:
        return "No Encounter Loaded"
    loot_table = Current_Encounter.generate_loot()
    eel.start('loot.html', port=8001)


@eel.expose
def create_encounter(token_blueprint):
    print("Creating Encounter")
    print(token_blueprint)
    encounter = Encounter(token_blueprint)
    return True


@eel.expose
def add_to_encounter(encounter_id, token_blueprint):
    encounter = [x for x in get_all_encounters() if x.id == encounter_id][0]
    encounter.add_tokens(token_blueprint)
    print("Adding to Encounter")
    return


def encounter_selection_block(x):
    return f"""
    <div class="encounter_block" onclick="load_encounter('{x.id}')">
    
    <input class="encounter-name text-seemless light" id='ename{x.id}' type='text' onchange=
    "change_e_name('{x.id}', 'ename{x.id}', null)" value='{x.name}'>
    
    </div>
    """


Encounter_Object_List = None
Current_Encounter = None


@eel.expose
def get_current_encounter():
    return Current_Encounter


def get_all_encounters(reload=False):
    global Encounter_Object_List
    if Encounter_Object_List is None or reload:
        this_dir, this_filename = os.path.split(__file__)
        save_path = os.path.join(this_dir, 'saves')
        file_path = os.path.join(save_path, '*.encounter')
        Encounter_Object_List = [Encounter.load(file) for file in glob.glob(file_path)]

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
    buttons = [f"""
    <div class="selected_encounter">
    <div class='button_wrap'>
    <input class="encounter_name dark text-seemless" id='ename{encounter.id}_1' type='text' onchange=
    "change_e_name('{encounter.id}', 'ename{encounter.id}_1', null)" value='{encounter.name}'>
    </div>
    <div class='button_wrap'>
    <button class="button" onclick="openTokenForm()"><strong>Add Token</strong></button>
    <button class="button" onclick="openLootForm()"><strong>Loot Table</strong></button>
    <button class="button" onclick="deleteEncounter()"><strong>Delete</strong></button>
    </div>
    """]
    encounter_blocks = [token.token_block() for token in encounter.tokens]
    bottem_buttons = [f"""
    </div>
    <div class='al-right'>
    <button class="button" style='width: 50px;' onclick="rehighlight_token()"><strong>Return</strong></button>
    <button class="button" style='width: 50px;' onclick="highlight_token(get_next_token_id())"><strong>Next</strong></button>
    </div>
        """]
    all = buttons + encounter_blocks + bottem_buttons
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
def change_e_name(encounter_id, value):
    # find the encounter in Ecounter_Object_List
    encounter = [x for x in get_all_encounters() if x.id == encounter_id][0]
    encounter.delete()
    encounter.name = value
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

@eel.expose
def delete_encounter(encounter_id):
    encounter = [x for x in get_all_encounters() if x.id == encounter_id][0]
    encounter.delete()
