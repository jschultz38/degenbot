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
    match rink:
        case 'KVIC':
            gameurl = f'{baseurl}{Livebarn.KENT.value}'
        case 'KCI Smrt':
            gameurl = f'{baseurl}{Livebarn.SMART.value}'
        case 'KCI VMFH':
            gameurl = f'{baseurl}{Livebarn.VMFH.value}'
        case 'KCI Star':
            gameurl = f'{baseurl}{Livebarn.STAR.value}'
        case 'OVA':
            gameurl = f'{baseurl}{Livebarn.OVA.value}'
        case 'EVT COMM' | 'Everett Community Ice':
            gameurl = f'{baseurl}{Livebarn.EVCOMM.value}'
        case 'LIC':
            gameurl = f'{baseurl}{Livebarn.LIC.value}'
        case _:
            print(f'ERROR: Could not find the rink: {rink}')
    return gameurl


