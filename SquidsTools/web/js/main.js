function replace_item(encounter_id, token_id, item_id) {
        console.log('replace_item')
        eel.replace_item(encounter_id, token_id, item_id)().then(function (result) {
            refresh_stat_block();
            // refresh_encounter_list();
            refresh_encounter();
        });
    }

function change_t_init(encounter_id, token_id, inputid, value) {
    let new_value = (inputid === null) ? value : document.getElementById(inputid).value;
    eel.change_t_init(encounter_id, token_id, new_value)().then(function (result) {
        refresh_encounter_list();
        refresh_encounter();
    });
}


function change_t_hp(encounter_id, token_id, inputid, value) {
    let new_value = (inputid === null) ? value : document.getElementById(inputid).value;
    eel.change_t_hp(encounter_id, token_id, new_value)().then(function (result) {
        refresh_encounter_list();
        refresh_encounter();
    });
}

function change_t_name(encounter_id, token_id, inputid, value) {
    let new_value = (inputid === null) ? value : document.getElementById(inputid).value;
    eel.change_t_name(encounter_id, token_id, new_value)().then(function (result) {
        refresh_encounter_list();
        refresh_encounter();
    });
}

function change_e_name(encounter_id, inputid, value) {
    let new_value = (inputid === null) ? value : document.getElementById(inputid).value;
    eel.change_e_name(encounter_id, new_value)().then(function (result) {
        refresh_encounter_list();
        refresh_encounter();
    });
}


async function get_monster_list() {
    await eel.get_monster_list()().then(function (result) {
        console.log(result)
        $('.monster-selection').select2(
            {
                data: result
                // width: '100%'
            }
        );
    });
}

async function get_weapon_list() {
    await eel.get_weapon_list()().then(function (result) {
        $('.weapon-selection').select2(
            {
                data: result,
                width: '100%'
            }
        );
    });
}

function refresh_encounter_list() {
    eel.get_encounter_list()().then(function (result) {
        $('.encounter_selection').html(result)
    });
}

function deleteEncounter() {
    if (!confirm('Are you sure you want to delete this Encounter?')) {
                return
            }
    eel.delete_encounter(selected_encounter_id)().then(function (result) {
        refresh_encounter_list();
        selected_encounter_id = 0;
        refresh_encounter();
    });
}

function openShopForm() {
    eel.clear_shop_builder()().then(function (result) {
        $('#ShopInventory').html(result)
        document.getElementById("ShopInventory").style.display = "block";
    });
}

function closeShopForm() {
    document.getElementById("ShopInventory").style.display = "none";
}

function sendShopForm() {
    let n_uncommon = document.getElementById("num_uncommon").value;
    let n_common = document.getElementById("num_common").value;
    let n_mundane = document.getElementById("num_mundane").value;
    let n_common_spells = document.getElementById("num_scommon").value;
    let n_uncommon_spells = document.getElementById("num_suncommon").value;
    let n_common_potions = document.getElementById("num_pcommon").value;
    let n_uncommon_potions = document.getElementById("num_puncommon").value;

    eel.create_shop_inventory(n_mundane, n_common, n_uncommon, n_common_spells,
        n_uncommon_spells, n_common_potions, n_uncommon_potions)().then(function (result) {
        refresh_encounter_list()
        closeShopForm();
    });

}

function openLootForm() {
    eel.create_loot_table()().then(function (result) {
    });

    // eel.clear_loot_builder()().then(function (result) {
    //     $('#LootCreation').html(result)
    //     document.getElementById("LootCreation").style.display = "block";
    // });
}

function closeLootForm() {
    document.getElementById("LootCreation").style.display = "none";
}

function sendLootForm() {
    let loot_roll = document.getElementById("loot_roll_number").value;
    let lootable_containers = document.getElementById("num_lootable").value;
    eel.create_loot_table(loot_roll, lootable_containers)().then(function (result) {
    });
    closeLootForm();
}

function openForm() {
    eel.clear_encounter_builder()().then(function (result) {
        $('#EncounterCreation').html(result)
        get_monster_list();
        document.getElementById("EncounterCreation").style.display = "block";
    });
}

function closeForm() {
    document.getElementById("EncounterCreation").style.display = "none";
}

function remove_entry() {
    console.log('remove_entry')
    console.log($(this))
    $(this).closest('tr').remove();
    console.log('remove_entry2')
}

async function addSelection() {
    let jsarr = $('#builder-monster-selection').select2('data');
    await eel.add_monster_to_encounter_builder(jsarr)().then(function (result) {
        let html = result[0];
        let weapon_list = result[1];
        console.log(html)
        console.log(weapon_list)
        $('#Encounter-Builder-Table > tbody:last-child').append(html)
        $('#Encounter-Builder-Table > tbody:last-child').find('.weapon-selection').select2(
            {
                data: weapon_list,
                width: '100%'
            });

        $(".remove_btn").click(function (event) {
            event.preventDefault();
            $(this).closest('tr').remove();
        });
    });
}

async function addTokenSelection() {
    let jsarr = $('#add-monster-selection').select2('data');
    await eel.add_monster_to_encounter_builder(jsarr)().then(function (result) {
        let html = result[0];
        let weapon_list = result[1];
        console.log(html)
        console.log(weapon_list)
        $('#Encounter-Add-Table > tbody:last-child').append(html)
        $('#Encounter-Add-Table > tbody:last-child').find('.weapon-selection').select2(
            {
                data: weapon_list,
                width: '100%'
            });

        $(".remove_btn").click(function (event) {
            event.preventDefault();
            $(this).closest('tr').remove();
        });
    });
}

function sendForm() {
    document.getElementById("EncounterCreation").style.display = "none";
    let arr = [];
    $('#Encounter-Builder-Table > tbody > tr').each(function (index, tr) {
        if (index === 0) {
            return;
        }
        if (index === 1) {
            let tds = $(this).find('td');
            let name = tds[0].innerText;
            let minions = parseInt(tds[2].getElementsByTagName('input')[0].value);
            arr.push({
                "name": name,
                "weapons": null,
                "minion_count": minions,
                "boss_count": null,
                "loot": null
            });
            return;
        }

        let tds = $(this).find('td');
        console.log(tds)
        let name = tds[0].innerText;
        let weapon = $(this).find(".weapon-selection").select2('data');
        // get juts the id from each weapon
        weapon = [].concat.apply([], weapon.map(function (x) {
            return x.id;
        }));
        let minions = parseInt(tds[2].getElementsByTagName('input')[0].value);
        let bosses = parseInt(tds[3].getElementsByTagName('input')[0].value);
        let loot = tds[4].getElementsByTagName('input')[0].checked;
        arr.push({
            "name": name,
            "weapons": weapon,
            "minion_count": minions,
            "boss_count": bosses,
            "loot": loot
        });

    });

    eel.create_encounter(arr)().then(function (result) {
        refresh_encounter_list();
    });

}


function openTokenForm() {
    eel.clear_add_token_builder()().then(function (result) {
        $('#AddToken').html(result)
        get_monster_list();
        document.getElementById("AddToken").style.display = "block";
    });
}

function closeTokenForm() {
    document.getElementById("AddToken").style.display = "none";
}

function sendTokenForm() {
    document.getElementById("AddToken").style.display = "none";
    let arr = [];
    $('#Encounter-Add-Table > tbody > tr').each(function (index, tr) {
        if (index === 0) {
            return;
        }
        if (index === 1) {
            let tds = $(this).find('td');
            let name = tds[0].innerText;
            let minions = parseInt(tds[2].getElementsByTagName('input')[0].value);
            arr.push({
                "name": name,
                "weapons": null,
                "minion_count": minions,
                "boss_count": null,
                "loot": null
            });
            return;
        }

        let tds = $(this).find('td');
        console.log(tds)
        let name = tds[0].innerText;
        let weapon = $(this).find(".weapon-selection").select2('data');
        // get juts the id from each weapon
        weapon = [].concat.apply([], weapon.map(function (x) {
            return x.id;
        }));
        let minions = parseInt(tds[2].getElementsByTagName('input')[0].value);
        let bosses = parseInt(tds[3].getElementsByTagName('input')[0].value);
        let loot = tds[4].getElementsByTagName('input')[0].checked;
        arr.push({
            "name": name,
            "weapons": weapon,
            "minion_count": minions,
            "boss_count": bosses,
            "loot": loot
        });

    });

    eel.add_to_encounter(selected_encounter_id, arr)().then(function (result) {
        refresh_encounter_list();
        refresh_encounter();
    });

}
