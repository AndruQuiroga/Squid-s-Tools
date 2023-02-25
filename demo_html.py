import eel
from html_utils import *

# Set web files folder and optionally specify which file types to check for eel.expose()
#   *Default allowed_extensions are: ['.js', '.html', '.txt', '.htm', '.xhtml']
eel.init('web', allowed_extensions=['.js', '.html'])

@eel.expose
def get_stat_block():
    return """
        <div contenteditable="true"  style="width:310px; font-family:Arial,Helvetica,sans-serif;font-size:11px;">
        <div class="name">Ogre</div>
        <div class="description">Large giant, chaotic evil</div>
        
        <div class="gradient"></div>
        
        <div>
            <div ><span class="bold red">Armor Class</span><span> 11 (hide armor)</span></div>
            <div><span class="bold red">Hit Points</span><span> 59 (7d10+21)</span></div>
            <div><span class="bold red">Speed</span><span> 40 ft.</span></div>
        </div>
        
        <div class="gradient"></div>
        
        <table>
            <tr><th>STR    </th><th>DEX   </th><th>CON    </th><th>INT   </th><th>WIS   </th><th>CHA   </th></tr>
            <tr><td>19 (+4)</td><td>8 (-1)</td><td>16 (+3)</td><td>5 (-3)</td><td>7 (-2)</td><td>7 (-2)</td></tr>
        </table>
            
        <div class="gradient"></div>
            
        <div><span class="bold">Senses</span><span> darkvision 60ft., passive Perception 8</span></div>
        <div><span class="bold">Languages</span><span> Common, Giant</span></div>
        <div><span class="bold">Challenge</span><span> 2 (450 XP)</span></div> 
            
        <div class="gradient"></div>
        
        <div class="actions red">Actions</div>
            
        <div class="hr"></div>
         
        <div class="attack"><span class="attackname">Greatclub.</span><span class="description"> Melee Weapon Attack:</span><span>+6 to hit, reach 5 ft., one target.</span><span class="description">Hit:</span><span>13 (2d8+4) bludgeoning damage.</span></div>    
        <div class="attack"><span class="attackname">Javelin.</span><span class="description"> Melee or Ranged Weapon Attack:</span><span>+6 to hit, reach 5 ft. or 30ft./120, one target.</span><span class="description">Hit:</span><span>11 (2d6+4) piercing damage.</span></div>    
        </div>
        """

# say_hello_py('Python World!')
# eel.say_hello_js('Python World!')   # Call a Javascript function

eel.start('index.html')