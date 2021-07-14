from typing import Dict, Union

ScrapeDict = Dict[str, Union[str, None]]

Number = Union[float, int]

line_breaker = '\n\n'

source_number_location_dict = {
    'commercial': {
        'valuation': "X",
        'actual': 'AG'
    },
    'office': {
        'valuation': 'Y',
        'actual': 'AH'
    },
    'residential': {
        'valuation': "Z",
        'actual': 'AI'
    },
    'sa': {
        'valuation': 'AA',
        'actual': 'AJ'
    }
}

result_number_location_dict = {
    'commercial': 'S',
    'office': 'T',
    'residential': 'U',
    'sa': 'V'
}


class ScrapeError(Exception):
    pass


class FormatError(Exception):
    pass


# user_agents = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
# ]
