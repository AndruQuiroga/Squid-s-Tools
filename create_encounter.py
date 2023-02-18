from loot_utils import Money, Inventory, Encounter, LifeStyle


if __name__ == '__main__':
    # ask if you want a default token
    if input('Use a specific monster? (y/n): '):
        default_token = input('Enter monster name: ')

    # ask for number of enemies
    num_enemies = int(input('Enter number of enemies: '))

    # ask for number of bosses
    num_bosses = input('Enter number of bosses (Default 1): ')
    if num_bosses == "":
        num_bosses = 1

    num_bosses = int(num_bosses)

    x = Encounter(base_token=default_token, num_boss_tokens=num_bosses, num_minion_tokens=num_enemies - num_bosses)

    # pickle the encounter
    import pickle
    with open(f'{default_token}.pkl', 'wb') as f:
        pickle.dump(x, f)

    print(f"Created {default_token}.html")
