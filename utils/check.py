from datetime import date
from dateutil.relativedelta import relativedelta


def check_dates_within(input_date: date, post_date: date):
    max_date = input_date + relativedelta(months=+3)
    min_date = input_date + relativedelta(months=-3)
    if max_date > post_date > min_date:
        return True
    return False


def check_is_residential(house_type: str):
    if house_type == 'sa' or house_type == 'residential':
        return True
    return False
