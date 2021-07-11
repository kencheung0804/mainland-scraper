import random
import time
import re
from typing import Optional

from constants.index import user_agents


def random_sleep():
    time.sleep(random.uniform(2, 10))
    return


def generate_init_headers():
    headers = {'User-Agent': random.choice(user_agents)}
    return headers


def input_loop(input_instruction: str, re_pattern: str,
               error_message: Optional[str] = 'Something is wrong. Please enter again!'):
    result = input(input_instruction)

    while not bool(re.search(re_pattern, result)):
        print(error_message)
        result = input_loop(input_instruction, re_pattern, error_message)

    return result
