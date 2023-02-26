from collections import defaultdict
from datetime import datetime

import pandas as pd


from classes_for_statement import Dividend, Buy_sell, Comission, Something, Dividend_with_tax, Dividend_zero_tax, \
    FINANCE_TYPE, INPUT_TYPE, OUTPUT_TYPE

INPUT_TYPE, OUTPUT_TYPE, FINANCE_TYPE

dict_shares = defaultdict(list)

def create_pd(list_of_rows):
    # csv_dict = []
    # for file_ in list_of_file:
    #     csv_dict.extend(read_file(file_))
    #     csv_dict = sorted(csv_dict, key=lambda d: datetime.strptime(d['date_'], '%d.%m.%Y'))
    csv_dict = []
    csv_dict.extend(list_of_rows)
    csv_dict = sorted(csv_dict, key=lambda d: datetime.strptime(d['date_'], '%d.%m.%Y'))


    for row_ in csv_dict:
        if 'dividend' in row_['description']:
            # line = Dividend(**row_)
            if 'tulumaks 0.00' in row_['description']:
                line = Dividend_zero_tax(**row_)
            else:
                line = Dividend_with_tax(**row_)
        elif 'K: ' in row_['description']:
            line = Comission(**row_)
        elif '@' in row_['description']:
            line = Buy_sell(**row_)
        else:
            line = Something(**row_)

        list_new_columns = ['month_', 'quart', 'year_', 'eursumm', 'firma_nr', 'firma_long',
                            'div_eur', 'tulumaks_eur', 'muud_kinni_eur', 'ticker_',
                            'amount_shares', 'price_shares', 'sanc', 'owner']
        for nc in list_new_columns:
            exec(f'row_["{nc}"] = line.{nc}')

        row_['class'] = line.__class__.__name__
        row_['type'] = line.report_type



        s_q_e = dict_shares.get(line.firma_long, '')

        q_total = sum([s_q_e[i].qnt for i in range(len(s_q_e)) if s_q_e[i].owner == row_['owner']])
        e_total = sum([s_q_e[i].amount for i in range(len(s_q_e)) if s_q_e[i].owner == row_['owner']])
        row_['shares_qnt'] = q_total
        row_['shares_eur'] = e_total


    df_full = pd.DataFrame(csv_dict)
    df_full['next_row'] = df_full['class'].shift(-1)
    return df_full