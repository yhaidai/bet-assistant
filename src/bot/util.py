from json import dumps


def bets_to_json_strings(bets):
    """
    Convert bets dictionary to json strings

    :param bets: bets dictionary
    :type bets: dict
    :return: json strings, one for each bet title
    :rtype: str
    """
    result = []

    for match_title in bets.keys():
        json_str = '*' + match_title.upper() + ':*\n' + dumps(bets[match_title], indent=4) + '\n\n'
        json_str = json_str.replace('"', '').replace('{', '').replace('}', '').replace(',', '\n')
        lines = json_str.split('\n')
        non_empty_lines = [line for line in lines if line.strip() != '']

        json_str = ''
        for line in non_empty_lines:
            json_str += line + '\n'

        result.append(json_str)

    return result
