from enum import Enum


class Livebarn(Enum):
    KENT = 1276
    AOTW = 1686
    EVCOMM = 1687
    VMFH = 2272
    STAR = 2270
    SMART = 2271
    LIC = 893
    OVA = 761
    RENTON_SMALL = 1048
    RENTON = 1047
    SNOQUALMIE_A = 1533
    SNOQUALMIE_B = 1532


def construct_gameurl(rink):
    baseurl = 'https://livebarn.com/en/video/'
    gameurl = ''

    rink_mapping = {
        'KVIC': Livebarn.KENT,
        'KCI Smrt': Livebarn.SMART,
        'KCI VMFH': Livebarn.VMFH,
        'KCI Star': Livebarn.STAR,
        'OVA': Livebarn.OVA,
        'EVT COMM': Livebarn.EVCOMM,
        'Everett Community Ice': Livebarn.EVCOMM,
        'LIC': Livebarn.LIC
    }

    if rink in rink_mapping:
        gameurl = f'{baseurl}{rink_mapping[rink].value}'
    else:
        print(f'ERROR: Could not find the rink: {rink}')

    return gameurl