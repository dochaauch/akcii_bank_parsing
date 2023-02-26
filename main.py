import pandas as pd
import numpy as np
import sidetable

from datetime import datetime, date
import csv

import ticker_dict

from collections import defaultdict

import os

from classes_for_statement import Dividend, Buy_sell, Comission, Something, Dividend_with_tax, Dividend_zero_tax

import pprint


#в этих папках не должно быть вложений и только нужные csv
your_target_folder_list = [
    "/Users/docha/Google Диск/akcii Tolika/2022",
                            "/Users/docha/Google Диск/akcii Tolika/2021",
                           "/Users/docha/Google Диск/akcii docha/2022"]
list_of_file = []

def read_all_files_in_folder(fold_list):
    for folder_ in fold_list:
        for dirpath, _, filenames in os.walk(folder_):
            for items in filenames:
                file_full_path = os.path.abspath(os.path.join(dirpath, items))
                if file_full_path.endswith('.csv'):
                    list_of_file.append(file_full_path)
    return list_of_file

#list_of_file = ['tolik_210101-211231_aa.csv',
#                'tolik_220101-220630_aa.csv',
#                'tolik_220701-220706_aa.csv',
#                'docha_220101-220630.csv']

list_of_file = read_all_files_in_folder(your_target_folder_list)
print(list_of_file)

dict_shares = defaultdict(list)


def read_file(file_):
    with open(file_) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';',
                    fieldnames=("cus_account", "string_type", "date_"," Receiver_payer", "description", "amount",
                                "currency", "debit_credit", "archive_attribute", "trans_type", "ref_nr", "doc_nr",
                                "emp"))
        next(csv_reader)  # пропустить строку с заголовками
        list_of_rows_ = list(csv_reader)
        list_of_rows = sorted(list_of_rows_, key=lambda d: datetime.strptime(d['date_'], '%d.%m.%Y'))
        return list_of_rows


csv_dict = []
for file_ in list_of_file:
    csv_dict.extend(read_file(file_))
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

print("Whithout something")
print(df_full[(df_full['class'] != 'Something') & (df_full['ticker_'] == '')].to_string(), end='\n\n')

#сохранить df в csv
#df_full.to_csv("combine.csv")

#распечатка всех данных
#print("All data ")
#print(df_full.to_string(), end='\n\n')

#выборка по определенному тикеру
for key in sorted(ticker_dict.ticker_dict.keys()):
    df4 = df_full[df_full['ticker_'] == key]
    pd.options.mode.chained_assignment = None # disable chained assignments, для добавления Total,
    # SettingWithCopyWarning
    df4.loc['Total'] = df4.sum(numeric_only=True)
    df4 = df4.replace(np.nan, '', regex=True)
    print('-------')
    print('выборка по тикеру ', key)
    print(df4.to_string(), end='\n\n')


df_buy_sel_div = df_full[(df_full['class'] == 'Buy_sell') | (df_full['class'] .str.startswith('Dividend'))]
print('Buy - sell - dividend, вложенная сумма по владельцу')
print(df_buy_sel_div.groupby(['owner']).agg({'eursumm': ['sum']}).stb.subtotal(), end='\n\n')

df_buy_sel_div = df_buy_sel_div.groupby(['sanc', 'owner'])
print('Buy - sell - dividend, вложенная сумма по владельцу, санкционные')
print(df_buy_sel_div.agg({'eursumm': ['sum']}).stb.subtotal(), end='\n\n')

print('***')
df_buy_sell = df_full[(df_full['class'] == 'Buy_sell')]
print('Buy - sell', 'всего вложено, без учета дивидендов')
print(df_buy_sell.agg({'eursumm': ['sum']}).groupby(['owner']).sum(), end='\n\n')
df_buy_sell_sanc_own = df_buy_sell.groupby(['sanc', 'owner'])
print('Buy - sell', 'всего вложено, без учета дивидендов, по владельцам и санцкиям')
print(df_buy_sell_sanc_own.agg({'eursumm': ['sum']}).stb.subtotal(), end='\n\n')

print('***')
print('Buy - sell', 'всего вложено, без учета дивидендов, ticker')
print(df_buy_sell.groupby(['ticker_', 'owner']).agg({'eursumm': ['sum']}).stb.subtotal().to_string(), end='\n\n')




agg_func_math = {
        'eursumm': ['sum']
    }
df_dividend = df_full[(df_full['class'] .str.startswith('Dividend'))]


agg_for_div = {'div_sum_':('eursumm','sum'),
               'sh_qnt_last':('shares_qnt','last'),
               'sh_sum_last':('shares_eur','last')}


by_firma = df_dividend.groupby(['firma_long', 'owner']).agg(**agg_for_div).round(2).stb.subtotal()
by_firma['yield'] = round(by_firma.div_sum_ / by_firma.sh_sum_last * -1 * 100, 4)

print('дивиденды по фирмам')
print(by_firma.to_string(), end='\n\n')

by_firma1 = by_firma[by_firma['yield']>= 3]
print('прибыль больше 3')
print(by_firma1.to_string(), end='\n\n')

by_firma1 = by_firma[by_firma['yield'] < 3]
print('прибыль меньше 3')
print(by_firma1.to_string(), end='\n\n')


by_year = df_dividend.groupby(['year_']).agg(agg_func_math).round(2)
print('дивиденды по годам')
print(by_year, end='\n\n')

by_year_firma = df_dividend.groupby(['year_', 'firma_long']).agg(agg_func_math).round(2).stb.subtotal()
print('дивидены фирма год')
print(by_year_firma, end='\n\n')

by_month = df_dividend.groupby(['owner','month_']).agg(agg_func_math).round(2)
by_month.loc['Всего дивиденды'] = by_month.sum()
print('дивидены по месяцам и владельцам: ')
print(by_month, end='\n\n')


#или комиссия или акции без комиссии
#чтобы найти, когда количество акций будет 0, чтобы взять остаточное сальдо
df_comm = df_full[(df_full['class'] == 'Comission') |
                  ((df_full['class'] == 'Buy_sell') & (df_full['next_row'] != 'Comission'))]

fix_shares_df = df_comm[(df_comm['shares_qnt'] == 0)]
#fix_shares_df_firma = fix_shares_df.groupby('firma_long')['shares_eur'].agg('sum').round(2)
#fix_shares_df_firma.loc["Фиксация всего"] = fix_shares_df_firma.sum()

fix_shares_df_firma = pd.crosstab(fix_shares_df['firma_long'], fix_shares_df['year_'],
                    values=round(fix_shares_df['shares_eur'], 2),
                    aggfunc='sum', margins=True, margins_name='Total').fillna('')
print('фиксация, все акции, и те, что с комиссией и без')
print(fix_shares_df_firma, end='\n\n')


df_cross_dividend = pd.crosstab(df_dividend['firma_long'], df_dividend['year_'],
                       values=round(df_dividend['eursumm'], 2),
                       aggfunc='sum', margins=True, margins_name='Total').fillna('')
print('дивиденды')
print(df_cross_dividend, end='\n\n')

df_cross_dividend_owner = pd.crosstab(df_dividend['firma_long'], [df_dividend.year_, df_dividend.owner],
                       values=round(df_dividend['eursumm'], 2),
                       rownames=['firma'],
                       colnames=['year', 'who'],
                       aggfunc=np.sum, margins=True, margins_name='Total').fillna('-')

print('дивиденды по годам и пользователям')
print(df_cross_dividend_owner.to_string(), end='\n\n')


#все цифры округляем до 2 знаков после запятой
df_dividend = np.round(df_dividend, decimals=2)
pvt = df_dividend.pivot_table(index=['firma_long'],
                    columns=['year_', 'month_'],
                    values=['eursumm'],
                    margins=False,  aggfunc=np.sum, fill_value=0)

subtotal_cols = pvt.groupby(level=1, axis=1).sum() #создаем столбец с промежуточной суммой
#переименовываем столбцы, чтобы присоединить к сводной таблице
subtotal_cols.columns = pd.MultiIndex.from_arrays([len(subtotal_cols.columns) * ['eursumm'],
                                                 subtotal_cols.columns, len(subtotal_cols.columns) * ['SUBT']])
#добавить столбецы к таблице
pvt = pvt.join(subtotal_cols).sort_index(axis=1)

#добавить итоговую строку
pvt.loc['Total per month'] = pvt.sum()
#добавить итоговый столбец. делим сумму на 2, потому что туда добавлены и промежуточные суммы
pvt.loc[:,('eursumm','TOTAL','')] = pvt.sum(axis=1)/2
#меняем все 0 на прочерк
pvt[pvt.eq(0)] = '-'
print('дивиденды по месяцам и годам, все вместе')
print(pvt.to_string(), end='\n\n')







