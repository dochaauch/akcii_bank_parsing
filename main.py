import pandas as pd
import numpy as np
import sidetable

from datetime import datetime, date
import csv
import re

from currency_converter import CurrencyConverter
import ticker_dict

from collections import namedtuple
from collections import defaultdict


#import yfinance as yf
#from yahoofinancials import YahooFinancials

import pprint



#tickerSymbol = 'TKM1T'
#tickerData = yf.Ticker(tickerSymbol)
#pprint.pprint(tickerData.info)
#print(tickerData.info['shortName'])


#yf = YahooFinancials('EARN')
#print(yf.__doc__)


#update course
#from currency_converter import ECB_URL, SINGLE_DAY_ECB_URL
# Download the full history, this will be up to date. Current value is:
# https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip
#c = CurrencyConverter(ECB_URL)


c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_wrong_date=True)

Moving = namedtuple('Moving', 'date_ qnt amount owner')

#file_ = 'tolik_21_22.csv'
#file_ = 'docha_2022.csv'
list_of_file = ['tolik_210101-211231_aa.csv',
                'tolik_220101-220630_aa.csv',
                'tolik_220701-220706_aa.csv',
                'docha_2022.csv']

dict_shares = defaultdict(list)


def read_file(file_):
    with open(file_) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';',
                    fieldnames=("cus_account", "string_type", "date_"," Receiver_payer", "description", "amount",
                                "currency", "debit_credit", "archive_attribute", "trans_type", "ref_nr", "doc_nr",
                                "emp"))
        next(csv_reader) # пропустить строку с заголовками
        list_of_rows_ = list(csv_reader)
        list_of_rows = sorted(list_of_rows_, key=lambda d: datetime.strptime(d['date_'], '%d.%m.%Y'))
        return list_of_rows


class Selgitus():
    #__slots__ = ["Счëт клиентa","Строковый тип","Дата","Получатель/Плательщик","Пояснение",
    #"Сумма","Currency","Дебит/Кредит","Архивный признак","Тип сделки","Номер ссылки","Номер документа",]
    __slots__ = ["cus_account", "string_type", "date_", "Receiver_payer", "description", "amount", "currency",
    "debit_credit", "archive_attribute", "trans_type", "ref_nr", "doc_nr", "emp"]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.date_ = datetime.strptime(self.date_, '%d.%m.%Y')
        self.month_ = self.date_.strftime('%Y-%m')
        self.year_ = str(self.date_.year)
        self.amount = float(self.amount.replace(',', '.'))

    @property
    def eursumm(self):
        eursumm = self.amount
        if self.currency != 'EUR':
            eursumm = c.convert(self.amount, self.currency, 'EUR', date=self.date_)
        if self.debit_credit == 'D':
            eursumm = - eursumm
        return eursumm


    @property
    def quart(self):
        #date_month = int(self.date_.strftime('%m'))
        date_month = self.date_.month
        if 1 <= date_month <= 3:
            return f'{self.date_.year}-Q1'
        if 4 <= date_month <= 6:
            return f'{self.date_.year}-Q2'
        if 7 <= date_month <= 9:
            return f'{self.date_.year}-Q3'
        if 10 <= date_month <= 12:
            return f'{self.date_.year}-Q4'

    @property
    def firma_nr(self):
        return ''

    @property
    def firma_long(self):
        return ''

    @property
    def div_eur(self):
        return 0.00

    @property
    def tulumaks_eur(self):
        return 0.00

    @property
    def muud_kinni_eur(self):
        return 0.00

    @property
    def ticker_(self):
        return ''

    @property
    def amount_shares(self):
        return 0

    @property
    def price_shares(self):
        return ''

    @property
    def sanc(self):
        return ''

    @property
    def owner(self):
        if self.cus_account == 'EE832200221010052801':
            return 'tolik'
        elif self.cus_account == 'EE272200221078511559':
            return 'docha'
        else:
            return 'NOT FOUND!'



class Dividend(Selgitus):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def firma_nr(self):
        nr_firma_pattern = r'/\d+/\s(\b\w*)'
        return re.findall(nr_firma_pattern, self.description)[0].strip()

    @property
    def firma_long(self):
        firma_pattern = rf'/\d+/\s\b\w*(.*)dividend'
        return re.findall(firma_pattern, self.description)[0].strip()

    @property
    def div_eur(self):
        self.curr_patt = r"\d{1,}.\d{2}\s(\w{3})"
        currency_div_pattern = f'dividend {self.curr_patt},'
        currency_div = re.findall(currency_div_pattern, self.description)[0].strip()

        self.digit_pattern = r"(\d{1,}.\d{2})\s\w{3}"
        summa_div_pattern = f'dividend {self.digit_pattern},'
        div_amount = float(re.findall(summa_div_pattern, self.description)[0])
        if currency_div == 'EUR':
            return div_amount
        else:
            return c.convert(div_amount, currency_div, 'EUR', line.date_)

    @property
    def tulumaks_eur(self):
        tulumaks_currency_pattern = f'tulumaks {self.curr_patt}'
        tulumaks_currency = re.findall(tulumaks_currency_pattern, self.description)[0].strip()

        tulumaks_pattern = f'tulumaks {self.digit_pattern}'
        tulumaks = float(re.findall(tulumaks_pattern, self.description)[0])

        if tulumaks_currency == 'EUR':
            return tulumaks
        else:
            return c.convert(tulumaks, tulumaks_currency, 'EUR', line.date_)

    @property
    def muud_kinni_eur(self):
        muud_kinni_pattern = f'muud kinnipidamised {self.digit_pattern}'
        if len(re.findall(muud_kinni_pattern, self.description)) > 0:
            muud_kinni = float(re.findall(muud_kinni_pattern, self.description)[0])
            muud_kinni_cur_pattern = f'muud kinnipidamised {self.curr_patt}'
            muud_kinni_cur = re.findall(muud_kinni_cur_pattern, self.description)[0].strip()
            if muud_kinni_cur == 'EUR':
                return muud_kinni
            else:
                return c.convert(muud_kinni, muud_kinni_cur, 'EUR', line.date_)
        else:
            return 0.00

    @property
    def ticker_(self):
        for key, value in ticker_dict.ticker_dict.items():
            if self.firma_long == value.full_name:
                return key

    @property
    def sanc(self):
        return ticker_dict.ticker_dict[self.ticker_].sanction





class Buy_sell(Selgitus):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        dict_shares[self.firma_long].append(Moving(self.date_, self.amount_shares, self.eursumm, self.owner))

    @property
    def ticker_(self):
        firma_pattern = r'(.*)\s[+-]\d{1,}@\d{1,}.*/'
        return re.findall(firma_pattern, self.description)[0].strip()

    @property
    def amount_shares(self):
        amount_shares_pattern = r'.*\s([+-]\d{1,})@\d{1,}.*/'
        return int(re.findall(amount_shares_pattern, self.description)[0])

    @property
    def price_shares(self):
        price_of_shares_pattern = r'.*\s[+-]\d{1,}@(\d{1,}.*)/'
        return re.findall(price_of_shares_pattern, self.description)[0].strip()

    @property
    def firma_long(self):
        return ticker_dict.ticker_dict[self.ticker_].full_name

    @property
    def sanc(self):
        return ticker_dict.ticker_dict[self.ticker_].sanction



class Comission(Selgitus):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        dict_shares[self.firma_long].append(Moving(self.date_, 0, self.eursumm, self.owner))

    @property
    def ticker_(self):
        firma_pattern = r'K: (.*)\s[+-]\d{1,}@\d{1,}.*/'
        return re.findall(firma_pattern, self.description)[0].strip()

    @property
    def firma_long(self):
        return ticker_dict.ticker_dict[self.ticker_].full_name

    @property
    def sanc(self):
        return ticker_dict.ticker_dict[self.ticker_].sanction





class Something(Selgitus):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

csv_dict = []
for file_ in list_of_file:
    csv_dict.extend(read_file(file_))
    csv_dict = sorted(csv_dict, key=lambda d: datetime.strptime(d['date_'], '%d.%m.%Y'))


for row_ in csv_dict:
    if 'dividend' in row_['description']:
        line = Dividend(**row_)
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



    s_q_e = dict_shares.get(line.firma_long, '')

    q_total = sum([s_q_e[i].qnt for i in range(len(s_q_e)) if s_q_e[i].owner == row_['owner']])
    e_total = sum([s_q_e[i].amount for i in range(len(s_q_e)) if s_q_e[i].owner == row_['owner']])
    row_['shares_qnt'] = q_total
    row_['shares_eur'] = e_total


df_full = pd.DataFrame(csv_dict)
df_full['next_row'] = df_full['class'].shift(-1)
#распечатка всех данных
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


df2 = df_full[(df_full['class'] == 'Buy_sell') | (df_full['class'] == 'Dividend')]
print('Buy - sell - dividend, вложенная сумма по владельцу')
print(df2.groupby(['owner']).agg({'eursumm': ['sum']}).stb.subtotal(), end='\n\n')

df2 = df2.groupby(['sanc', 'owner'])
print('Buy - sell - dividend, вложенная сумма по владельцу, санкционные')
print(df2.agg({'eursumm': ['sum']}).stb.subtotal(), end='\n\n')

print('***')
df3 = df_full[(df_full['class'] == 'Buy_sell')]
print('Buy - sell', 'всего вложено, без учета дивидендов')
print(df3.agg({'eursumm': ['sum']}).groupby(['owner']).sum(), end='\n\n')
df5 = df3.groupby(['sanc', 'owner'])
print('Buy - sell', 'всего вложено, без учета дивидендов, по владельцам и санцкиям')
print(df5.agg({'eursumm': ['sum']}).stb.subtotal(), end='\n\n')

print('***')
print('Buy - sell', 'всего вложено, без учета дивидендов, ticker')
print(df3.groupby(['ticker_', 'owner']).agg({'eursumm': ['sum']}).stb.subtotal().to_string(), end='\n\n')




agg_func_math = {
        'eursumm': ['sum']
    }
df_dividend = df_full[(df_full['class'] == 'Dividend')]


agg_for_div = {'div_sum_':('eursumm','sum'),
               'sh_qnt_last':('shares_qnt','last'),
               'sh_sum_last':('shares_eur','last')}


by_firma = df_dividend.groupby(['firma_long', 'owner']).agg(**agg_for_div).round(2).stb.subtotal()
by_firma['yield'] = round(by_firma.div_sum_ / by_firma.sh_sum_last * -1 * 100, 4)

print('дивиденды по фирмам')
print(by_firma.to_string(), end='\n\n')

by_firma1 = by_firma[by_firma['yield'] > 2]
print('прибыль больше 2')
print(by_firma1.to_string(), end='\n\n')


by_year = df_dividend.groupby(['year_']).agg(agg_func_math).round(2)
print('дивиденды по годам')
print(by_year, end='\n\n')

by_year_firma = df_dividend.groupby(['year_', 'firma_long']).agg(agg_func_math).round(2).stb.subtotal()
print('дивидены фирма год')
print(by_year_firma, end='\n\n')

by_month = df_dividend.groupby(['month_']).agg(agg_func_math).round(2)
by_month.loc['Всего дивиденды'] = by_month.sum()
print('дивидены по месяцам: ')
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
print('фиксация, акции с комиссией и без')
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
print('дивиденды по месяцам и годам')
print(pvt.to_string(), end='\n\n')







