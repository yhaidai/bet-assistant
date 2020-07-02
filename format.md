# Description of unified format to store information in

* ##csgo
    * ###match title:
        <first_team_name> - <second_team_name>  
        *names of the teams must be sorted in alphabetical order*
    * ###bet titles
        - #####Win:
            `<team_name>` will win
        - #####Total rounds/maps
            total `<over/under>` `<value>`
        - #####Total even/odd
            total — `even/odd`
        - #####Handicap rounds
            handicap `<team_name>` `<+/-value>`
        - #####Handicap maps
            `<team_name>` handicap `<+/-value>` maps
        - #####Map
            `<map_number>` map: `<suffix>`  
            `<map number>` - 1-st/2-nd/3-rd/4-th/5-th etc
        - #####Correct score
            correct score `value1`-`<value2>`
        - #####Win in specific round
            `<team_name>` will win in round `<value>`
