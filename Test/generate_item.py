import pandas as pd
from tabulate import tabulate

# load item csv
items = pd.read_csv('../SquidsTools/data/Items.csv')

if __name__ == '__main__':
    # ask user for rarity with numbers
    # 0 = mundane
    # 1 = common
    # 2 = uncommon

    print('0: Mundane')
    print('1: Common')
    print('2: Uncommon')

    rarity = int(input('Select a rarity: '))
    if rarity == 0:
        items = items[items['Rarity'] == 'none']
    elif rarity == 1:
        items = items[items['Rarity'] == 'common']
    elif rarity == 2:
        items = items[items['Rarity'] == 'uncommon']

    while True:
        # ranoomly select an item
        # ask user for d100
        # if d100 is in the range of the item, print the item
        # else, print a failure message
        input('Roll a d100:')
        item = items.sample()
        for column in item.columns:
            print(f'{column}: {item[column].values[0]}')
        if input('Another? (y/n): ') == 'n':
            break




