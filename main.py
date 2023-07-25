import csv
import os
from collections import defaultdict
from datetime import datetime

import numpy as np
import pandas as pd
import sidetable as stb

import classes_for_statement

from icecream import ic
from datetime import datetime

#stb.extension("pandas")

import ticker_dict
from classes_for_statement import Buy_sell, Comission, Something, Dividend_with_tax, Dividend_zero_tax

def time_format():
    return f'{datetime.now()}|> '

#в этих папках не должно быть вложений и только нужные csv
your_target_folder_list = [
    "/Users/docha/Library/CloudStorage/GoogleDrive-mob37256213753@gmail.com/Мой диск/akcii Tolika/2022",
    "/Users/docha/Library/CloudStorage/GoogleDrive-mob37256213753@gmail.com/Мой диск/akcii Tolika/2021",
    "/Users/docha/Library/CloudStorage/GoogleDrive-mob37256213753@gmail.com/Мой диск/akcii docha/2022",
    "/Users/docha/Library/CloudStorage/GoogleDrive-mob37256213753@gmail.com/Мой диск/akcii Tolika/2023",
    "/Users/docha/Library/CloudStorage/GoogleDrive-mob37256213753@gmail.com/Мой диск/akcii docha/2023",
]
list_of_file = []

def read_all_files_in_folder(fold_list):
    for folder_ in fold_list:
        for dirpath, _, filenames in os.walk(folder_):
            for items in filenames:
                file_full_path = os.path.abspath(os.path.join(dirpath, items))
                if file_full_path.endswith('.csv'):
                    list_of_file.append(file_full_path)
    return list_of_file


list_of_file = read_all_files_in_folder(your_target_folder_list)
print(list_of_file)

#dict_shares = defaultdict(list)
dict_shares = classes_for_statement.dict_shares
dict_saldo = classes_for_statement.dict_saldo
dict_money = classes_for_statement.dict_money
dict_source = classes_for_statement.dict_source


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

    # for_saldo = dict_saldo.get(line.firma_long, '')
    # for_mean = dict_shares.get(line.firma_long, '')
    #
    #
    # q_total = sum([for_saldo[i].sh_qnt for i in range(len(for_saldo)) if for_saldo[i].owner == row_['owner']])
    # e_total = sum([for_saldo[i].sh_amount for i in range(len(for_saldo)) if for_saldo[i].owner == row_['owner']])
    # row_['shares_qnt0'] = q_total
    # row_['shares_eur0'] = e_total

    # total_q_mean = sum([for_mean[i].sh_qnt for i in range(len(for_mean)) if for_mean[i].owner == row_['owner']])
    # total_e_mean = sum([for_mean[i].sh_amount for i in range(len(for_mean)) if for_mean[i].owner == row_['owner']])
    # try:
    #     row_['mean_price0'] = total_e_mean / total_q_mean * -1
    #     #при продаже всех акций в 0 обнуляем данные для подсчета средней цены
    #     if q_total == 0:
    #         if line.firma_long in dict_shares:
    #             dict_shares[line.firma_long] = [entry for entry in dict_shares[line.firma_long] if
    #                                             entry.owner != row_['owner']]
    # except:
    #     row_['mean_price0'] = 0


    row_['shares_qnt'] = line.shares_qnt
    row_['shares_eur'] = line.shares_eur
    row_['mean_price'] = line.mean_price
    line.clear_dict_shares()

    dict_shares[line.firma_long].append(line)

    print(line.date_, line.owner, line.__class__.__name__, line.ticker_, line.eursumm,
          dict_money[line.owner]['balances'], dict_source.get(line.owner, {}).get(line.ticker_, {}))



df_full = pd.DataFrame(csv_dict)
df_full['next_row'] = df_full['class'].shift(-1)

#ic(dict_money)

# Loop through each owner and print their balances
#for owner in classes_for_statement.owners:
#    ic("Owner:", owner)
#    balances = dict_money[owner]['balances']
#    for category, balance in balances.items():
#        ic(f"{category.capitalize()} balance:", balance)

print("Whithout something, будет распечатано, если есть ошибки")
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
#print(df_buy_sel_div.groupby(['owner']).agg({'eursumm': ['sum']}).stsib.subtotal(), end='\n\n')

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







