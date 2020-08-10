# Description of unified format to store information in

* ##csgo
    * ###match title:
        `<first_team_name>` - `<second_team_name>`
        *names of the teams must be sorted in alphabetical order*
    * ###bet titles
        - #####Win:
            `<team_name>` will win
        - #####Win in round
            `<team_name>` will win in round `<value>`
        - #####Win exact number of maps
            `<team_name>` will win `<value>` maps
        - #####Win at least number of maps
            `<team_name>` `<will/will not>` win at least `<value>` maps
        - #####First to win number of rounds
            `<team_name>` will be first to win `<value>` rounds
        - #####First kill in round
            `<team_name>` will kill first in round `<value>`
        - #####Total maps
            total maps `<over/under>` `<value>`
        - #####Total rounds
            total rounds `<over/under>` `<value>`
        - #####Total kills in round over/under
            total kills in round `value` `<over/under>` `<value>`
        - #####Individual total rounds/maps
            `<team_name>` total `<over/under>` `<value>`
        - #####Total rounds even/odd
            total rounds `even/odd`
        - #####Total maps even/odd
            total maps `even/odd`
        - #####Handicap rounds
            handicap `<team_name>` `<+/-value>` rounds
        - #####Handicap maps
            `<team_name>` handicap `<+/-value>` maps
        - #####Map
            `<map_number>` map: `<suffix>`  
            `<map_number>` - 1-st/2-nd/3-rd/4-th/5-th etc
        - #####Correct score
            correct score `<value1>`-`<value2>`
        - #####Bomb planted/not planted
            Bomb `<planted/not planted>` in round `value`
        - #####Bomb exploded/defused
            Bomb `<exploded/defused>` in round `value`
        - #####Overtime
            Overtime `<yes/no>`
        - #####first/second half
            `<first/second>` half 
        - #####terrorists/counter-terrorists 
            `<t/ct>` 
        - #####Draw
            draw will `<win/lose>`
* ##dota 2
    * ###match title:
        <first_team_name> - <second_team_name>  
        *names of the teams must be sorted in alphabetical order*
    * ###bet titles
        - #####Win:
            `<team_name>` will win
        - #####Win exact number of maps
            `<team_name>` will win `<value>` maps
        - #####Win at least number of maps
            `<team_name>` `<will/will not>` win at least `<value>` maps
        - #####First blood
            `<team_name>` first kill
        - ##### Total maps
            total maps `<over/under>` `<value>`
        - ##### Total kills over/under
            total kills `<over/under>` `<value>`
        - #####Most kills 
            `<team_name>` most kills
        - #####Handicap most kills 
            `<team_name>` handicap most kills `<+/-value>`
        - #####Total kills odd/even
            total kills `<odd/even>`
        - #####Individual total kills odd/even
          `<team_name>`  total kills `<odd/even>`
        - #####Individual total kills
            `<team_name>` total kills `<over/under>` `<value>`
        - #####Handicap kills
            `<team_name>` handicap `<+/-value>` kills
        - #####Handicap maps
            `<team_name>` handicap `<+/-value>` maps
        - #####Map
            `<map_number>` map: `<suffix>`  
            `<map_number>` - 1-st/2-nd/3-rd/4-th/5-th etc
        - #####Map duration
            duration `<over/under>` `<value>`
        - #####Correct score
            correct score `<value1>`-`<value2>`
        - #####Draw
            draw will `<win/lose>`
        - #####First to make number of kills
            `<team_name>` will first make `<value>` kills
        - #####First to destroy tower
            `<team_name>` will first destroy tower
        - #####First to kill roshan
            `<team_name>` will first kill roshan
        - #####Team to make N-th kill
            `<team_name>` will make kill `<value>`
        - #####Multi-kill
            `<team_name>` `<quadra/penta>` kill
* ##football
    * ###match title:
        <first_team_name> - <second_team_name>  
        *names of the teams must be sorted in alphabetical order*
    * ###bet titles
        - #####Win:
            `<team_name>` will win
        - #####Draw
            draw will win
        - #####first/second half
            ^1st/2nd half
        - #####total/handicap
            (1st/2nd half)? team_name? total/handicap 
        - ##### Double chance
            `<team_name>` will lose 
        - ##### Both teams to score
            both to score `<yes/no>`
        - #####Team to score
            `<team_name>` to score `<yes/no>`
        