import csv
from datetime import datetime
import pprint
import re
from collections import OrderedDict
from typing import List

import pandas as pd

import ticker_dict

from currency_converter import CurrencyConverter


c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_wrong_date=True)

# "dividend" and not "tulumaks 0.00"


# Define constants
FIELDNAMES = ["cus_account", "string_type", "date_", "Receiver_payer", "description", "amount",
              "currency", "debit_credit", "archive_attribute", "trans_type", "ref_nr", "doc_nr", "emp", "eursumm"]
REG_NR_REGEX = re.compile(r"/\d+/\s+(\w{10})")
COMPANY_REGEX = re.compile(r"\w{10}\s+(.*)\s+dividend")
DIVIDEND_REGEX = re.compile(r"dividend\s+([\d.]+)\s+(\w{3})")
TULUMAKS_REGEX = re.compile(r"tulumaks\s+([\d.]+)\s+(\w{3})")


def read_file(file_path: str) -> List[OrderedDict]:
    """Read CSV file and return a list of ordered dictionaries representing the rows.
    Args:
        file_path (str): Path to the CSV file.
    Returns:
        list: A list of ordered dictionaries representing the rows.
    """
    with open(file_path) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';', fieldnames=FIELDNAMES)
        next(csv_reader)  # пропустить строку с заголовками
        list_of_rows = list(csv_reader)
        list_of_rows = sorted(list_of_rows, key=lambda d: datetime.strptime(d['date_'], '%d.%m.%Y'))
    return list_of_rows


def filter_rows(list_of_rows: List[OrderedDict], search_word: str, flag: str) -> List[OrderedDict]:
    """Filter rows by a search word and a flag.

        Args:
            list_of_rows (list): A list of ordered dictionaries representing the rows.
            search_word (str): The search word to filter by. Here should be 'dividend'
            flag (str): The flag to filter by. Here '' for "tulumaks 0.00" or 'not' for "not tulumaks 0.00"

        Returns:
            list: A list of ordered dictionaries representing the filtered rows.
        """
    if flag == "not":
        result_rows = [d for d in list_of_rows
                       if (search_word in d['description']) and (not "tulumaks 0.00" in d['description'])]
    else:
        result_rows = [d for d in list_of_rows
                       if (search_word in d['description']) and ("tulumaks 0.00" in d['description'])]
    return result_rows


def find_country(company):
    for key, value in ticker_dict.ticker_dict.items():
        if company in value.full_name:
            country = value.country
    return country


def parse_row(row):
    parse_string = row['description']

    # find regular expression matches
    reg_nr_match = re.search(REG_NR_REGEX, parse_string)
    company_match = re.search(COMPANY_REGEX, parse_string)
    dividend_match = re.search(DIVIDEND_REGEX, parse_string)
    tulumaks_match = re.search(TULUMAKS_REGEX, parse_string)

    # create dictionary of matches
    result = {
        "reg_nr": reg_nr_match.group(1) if reg_nr_match else None,
        "company": company_match.group(1) if company_match else None,
        "country": find_country(company_match.group(1)) if company_match else None,
        "currency": row['currency'],
        "dividend": float(dividend_match.group(1)) if dividend_match else None,
        "date_": row['date_'],
        "tulumaks": float(tulumaks_match.group(1)) if tulumaks_match else None,
        "on_hand": float(row['amount'].replace(",", ".")),
        "tax_%": round((float(tulumaks_match.group(1)) if tulumaks_match else None)
                 / (float(dividend_match.group(1)) if dividend_match else None) * 100, 2),
        "div_eur": round(c.convert(float(dividend_match.group(1)), row["currency"], 'EUR',
                             date=datetime.strptime(row["date_"], '%d.%m.%Y')), 2),
    }
    return result


def create_df(dict_):
    df = pd.DataFrame(dict_)
    return df


def process_df(list_for_df, country):
    df = create_df(list_for_df)
    df["tax_%"] = df["tax_%"].apply(lambda x: '{:.2f}'.format(x))

    if country == "not_local":
        df = df.loc[df['country'] != 'Эстония']
    elif country == "local":
        df = df.loc[df['country'] == 'Эстония']
    else:
        df = df

    df["eur_cumsum"] = df["div_eur"].cumsum()

    df.to_csv("div.csv", index=False)

    total_row = {'reg_nr': 'Total',
                 'company': '',
                 'country': df['country'].nunique(),
                 'currency': df['currency'].nunique(),
                 'dividend': df['dividend'].sum(),
                 'date_': '',
                 'tulumaks': df['tulumaks'].sum(),
                 'on_hand': df['on_hand'].sum(),
                 'tax_%': df['tulumaks'].sum()/df['on_hand'].sum() * 100,
                 'div_eur': df['div_eur'].sum(),
                 'eur_cumsum': '',
                 }

    total_df = pd.DataFrame(total_row, index=[0])
    df = pd.concat([df, total_df], ignore_index=True)



    print(df.to_string())


def print_rows_of_list(list_of_filter_rows):
    for row in list_of_filter_rows:
        print(row['description'])
        print(row['date_'], row['amount'], row['currency'])
        pprint.pprint(parse_row(row))
        print()


def collect_rows(list_of_filter_rows):
    list_for_df = []
    for row in list_of_filter_rows:
        res = parse_row(row)
        list_for_df.append(res)
    return list_for_df


def nice_print(list_of_rows, message, search_word, flag, country):
    print("*" * 15)
    print(message)
    list_with_no_div = filter_rows(list_of_rows, search_word, flag)
    list_for_df_no = collect_rows(list_with_no_div)
    #print_rows_of_list(list_with_no_div)
    process_df(list_for_df_no, country)
    print("*" * 15)



def main():
    # target_file = '/Users/docha/Google Диск/akcii docha/2022/statement.csv'
    target_file = '/Users/docha/Google Диск/akcii Tolika/2022/statement.csv'
    list_of_rows = read_file(target_file)
    #nice_print(list_of_rows, message='dividends, no taxes', search_word='dividend',
    #           flag='', country='all')
    nice_print(list_of_rows, message='dividends, no taxes, local', search_word='dividend',
               flag='', country='local')
    nice_print(list_of_rows, message='dividends, no taxes, foreign', search_word='dividend',
               flag='', country='not_local')
    nice_print(list_of_rows, message='dividends, with taxes, for EMTA, local', search_word='dividend',
               flag='not', country='local')
    nice_print(list_of_rows, message='dividends, with taxes, for EMTA, foreign', search_word='dividend',
               flag='not', country='not_local')


if __name__ == '__main__':
    main()
