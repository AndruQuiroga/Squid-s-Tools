import eel as eel
import pandas as pd
base_html_stat_block = f"""
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
"""

end_html_stat_block = """
</body>
</html>
"""

monster_df = pd.read_csv('./data/Bestiary_filtered.csv')


@eel.expose
def get_monster_list():
    return [{"id": i, "text": x} for i, x in enumerate(monster_df['Name'])]


# <tr>
#           <td>MONSTER1</td>
#           <td><select class="js-example-basic-multiple" name="states[]" multiple="multiple"></select></td>
#           <td><select class="js-example-basic-single" placeholder="0"></select></td>
#           <td><select class="js-example-basic-single" placeholder="0"></select></td>
#           <td><input type="checkbox"></td>
#           <td><button type="button" class="btn">Remove</button></td>
#         </tr>
@eel.expose
def add_monster_to_encounter_builder(js_arr):
    monster_name = js_arr[0]['text']
    monster = monster_df[monster_df['Name'] == monster_name]
    s = "<tr>"
    s += f"<td>{monster['Name'].to_numpy()[0]}</td>"
    s += f"<td><select class=\"weapon-selection\"multiple=\"multiple\"></select></td>"
    s += f"<td><select class=\"js-example-basic-single\"></select></td>"
    s += f"<td><select class=\"js-example-basic-single\"></select></td>"
    s += "<td><input type=\"checkbox\"></td>"
    s += "<td><button type=\"button\" class=\"btn\">Remove</button></td>"
    s += "</tr>"
    return s


def token_block(i, token):
    return f"""
        <div contenteditable="true"  style="width:310px; font-family:Arial,Helvetica,sans-serif;font-size:11px;">
        <div class="name">{token.name}_{i}</div>
        <div class="description">None</div>

        <div class="gradient"></div>

        <div class="red">
            <div ><span class="bold red">Armor Class</span><span> {token.info['AC'].to_numpy()[0]}</span></div>
            <div><span class="bold red">Hit Points</span><input id=HP_{i} type="number" value="{token.hit_points}"></input></div>
            <div><span class="bold red">Speed</span><span> {token.info['Speed'].to_numpy()[0]}</span></div>
        </div>
        
        <button onclick="increment_{i}()">+</button>
        <button onclick="decrement_{i}()">-</button>

        <div class="gradient"></div>

        <table>
            <tr><th>STR    </th><th>DEX   </th><th>CON    </th><th>INT   </th><th>WIS   </th><th>CHA   </th></tr>
            <tr><td>{token.info['Strength'].to_numpy()[0]}</td><td>{token.info['Dexterity'].to_numpy()[0]}</td><td>{token.info['Constitution'].to_numpy()[0]}</td>
            <td>{token.info['Intelligence'].to_numpy()[0]}</td><td>{token.info['Wisdom'].to_numpy()[0]}</td><td>{token.info['Charisma'].to_numpy()[0]}</td></tr>
        </table>

        <div class="gradient"></div>

        <div><span class="bold">Senses</span><span>{token.info['Senses'].to_numpy()[0]}</span></div>
        <div><span class="bold">Languages</span><span>{token.info['Languages'].to_numpy()[0]}</span></div>
        <div><span class="bold">Challenge</span><span>{token.cr}</span></div> 

        <div class="gradient"></div>

        <div class="actions red">Actions</div>
        <p>{token.info['Actions'].to_numpy()[0]}</p>
        <div class="hr"></div>

        </div>
        """


# <div class="attack"><span class="attackname">Greatclub.</span><span class="description"> Melee Weapon Attack:</span><span>+6 to hit, reach 5 ft., one target.</span><span class="description">Hit:</span><span>13 (2d8+4) bludgeoning damage.</span></div>
# <div class="attack"><span class="attackname">Javelin.</span><span class="description"> Melee or Ranged Weapon Attack:</span><span>+6 to hit, reach 5 ft. or 30ft./120, one target.</span><span class="description">Hit:</span><span>11 (2d6+4) piercing damage.</span></div>

def script_block(num_tokens):
    total_string = ""
    for i in range(num_tokens):
        total_string += f"""
        <script>
       function increment_{i}() {{
          document.getElementById('HP_{i}').stepUp();
       }}
       function decrement_{i}() {{
          document.getElementById('HP_{i}').stepDown();
       }}
    </script>
        """
    return total_string

def create_html_stat_block(tokens):
    # save the html file
    with open(f'{tokens[0].name}.html', 'w') as f:
        f.write(base_html_stat_block)
        for i in range(len(tokens)):
            f.write(token_block(i, tokens[i]))
        f.write(script_block(len(tokens)))
        f.write(end_html_stat_block)
