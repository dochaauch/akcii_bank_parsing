import re
from collections import defaultdict
from collections import namedtuple
from datetime import datetime

from currency_converter import CurrencyConverter

import ticker_dict

c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_wrong_date=True)
dict_shares = defaultdict(list)
dict_saldo = defaultdict(list)
Moving = namedtuple('Moving', 'date_ sh_qnt sh_amount owner')


# Define the owners
owners = ['tolik', 'docha']

# Create the nested defaultdict with the specified keys for each owner
dict_money = defaultdict(lambda: defaultdict(list))

# Add the four keys to each owner's dictionary
for owner in owners:
    dict_money[owner]['cash'] = []
    dict_money[owner]['div_with_tax'] = []
    dict_money[owner]['div_zero_tax'] = []
    dict_money[owner]['result'] = []
    dict_money[owner]['virt_wallet'] = []
    dict_money[owner]['balances'] = {
        'cash': 0.0,
        'div_with_tax': 0.0,
        'div_zero_tax': 0.0,
        'result': 0.0,
        'virt_wallet': 0.0}

Money_in_out = namedtuple('Money_in_out', 'date_ ticker amount_eur')

dict_source = {}
for owner in owners:
    dict_source[owner] = {}


INPUT_TYPE = 'input'
OUTPUT_TYPE = 'output'
FINANCE_TYPE = 'finance'


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

    def cash_flow(self, category):
        money_in_out_instance = Money_in_out(self.date_, self.ticker_, round(self.eursumm, 2))
        dict_money[self.owner][category].append(money_in_out_instance)
        # Update the balance for the specific category with two decimal places
        dict_money[self.owner]['balances'][category] = round(
            dict_money[self.owner]['balances'][category] + self.eursumm, 2)
        print("cash flow", self.date_, self.ticker_, category, self.owner, dict_money[self.owner]['balances'][category])

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

    @property
    def report_type(self):
        return ''

    @property
    def shares_qnt(self):
        for_saldo = dict_saldo.get(self.firma_long, '')
        return sum([for_saldo[i].sh_qnt for i in range(len(for_saldo)) if for_saldo[i].owner == self.owner])

    @property
    def shares_eur(self):
        for_saldo = dict_saldo.get(self.firma_long, '')
        return sum([for_saldo[i].sh_amount for i in range(len(for_saldo)) if for_saldo[i].owner == self.owner])

    @property
    def mean_price(self):
        for_mean = dict_shares.get(self.firma_long, '')
        qnt_values = [entry.sh_qnt for entry in for_mean if hasattr(entry, 'sh_qnt') and entry.owner == self.owner]
        total_q_mean = sum(qnt_values) if qnt_values else 0

        amount_values = [entry.sh_amount for entry in for_mean if hasattr(entry, 'sh_amount') and entry.owner == self.owner]
        total_e_mean = sum(amount_values) if amount_values else 0

        try:
            return total_e_mean / total_q_mean * -1
        except ZeroDivisionError:
            return 0

    def clear_dict_shares(self):
        if self.shares_qnt == 0:
            if self.firma_long in dict_shares:
                dict_shares[self.firma_long] = [entry for entry in dict_shares[self.firma_long] if
                                                entry.owner != self.owner]


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
            # return c.convert(div_amount, currency_div, 'EUR', line.date_)
            return c.convert(div_amount, currency_div, 'EUR', self.date_)

    @property
    def tulumaks_eur(self):
        tulumaks_currency_pattern = f'tulumaks {self.curr_patt}'
        tulumaks_currency = re.findall(tulumaks_currency_pattern, self.description)[0].strip()

        tulumaks_pattern = f'tulumaks {self.digit_pattern}'
        tulumaks = float(re.findall(tulumaks_pattern, self.description)[0])

        if tulumaks_currency == 'EUR':
            return tulumaks
        else:
            # return c.convert(tulumaks, tulumaks_currency, 'EUR', line.date_)
            return c.convert(tulumaks, tulumaks_currency, 'EUR', self.date_)

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
                # return c.convert(muud_kinni, muud_kinni_cur, 'EUR', line.date_)
                return c.convert(muud_kinni, muud_kinni_cur, 'EUR', self.date_)
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

    @property
    def report_type(self):
        return ''



class Buy_sell(Selgitus):
    balance_categories = ['result', 'div_zero_tax', 'div_with_tax', 'cash']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #собираем только покупку, для средней цены акции
        if self.amount_shares > 0:
            dict_shares[self.firma_long].append(Moving(self.date_, self.amount_shares, self.eursumm, self.owner))
        dict_saldo[self.firma_long].append(Moving(self.date_, self.amount_shares, self.eursumm, self.owner))

        if self.eursumm < 0:  # покупка акций
            self.buy_stocks(dict_money, dict_source)
        else:
            self.sell_stocks(dict_money, dict_source)

    def buy_stocks(self, dict_money, dict_source):
        remaining_eursumm = self.eursumm

        for category in self.balance_categories:
            balance = dict_money[self.owner]['balances'][category]

            if category != 'cash':
                if balance > 0:
                    if remaining_eursumm < 0:
                        # Check if the remaining amount can be fully closed from the current category
                        if remaining_eursumm + balance >= 0:
                            dict_money[self.owner]['balances'][category] += round(remaining_eursumm, 2)
                            dict_money[self.owner][category].append(
                                Money_in_out(self.date_, self.ticker_, round(remaining_eursumm, 2)))
                            remaining_eursumm = 0
                            break
                        else:
                            # Perform the closing from the current category balance
                            dict_money[self.owner]['balances'][category] = 0
                            remaining_eursumm += balance
                            dict_money[self.owner][category].append(
                                Money_in_out(self.date_, self.ticker_, round(balance, 2)))

        # If there is still a remaining negative amount, close it from the 'cash' category
        dict_money[self.owner]['balances']['cash'] += round(remaining_eursumm, 2)

        # Получаем текущие значения cash и virt_wallet с установкой значения по умолчанию 0.0
        current_cash, current_virt_wallet = dict_source[self.owner].get(self.ticker_,
                                                                        {'cash': 0.0, 'virt_wallet': 0.0}).values()

        # Вычисляем новые значения cash и virt_wallet
        new_cash, new_virt_wallet = current_cash + remaining_eursumm, current_virt_wallet + (
                    remaining_eursumm - self.eursumm)

        # Обновляем словарь с новыми значениями
        dict_source[self.owner][self.ticker_] = {'cash': new_cash, 'virt_wallet': new_virt_wallet}
        print('проверка', dict_source[self.owner][self.ticker_])
        dict_money[self.owner]['cash'].append(
            Money_in_out(self.date_, self.ticker_, round(remaining_eursumm, 2)))

    def sell_stocks(self, dict_money, dict_source):
        remaining_eursumm = self.eursumm
        mid_sale = round(self.mean_price * self.amount_shares, 2)
        result = round(remaining_eursumm - mid_sale * -1, 2)

        dict_money[self.owner]['result'].append(
            Money_in_out(self.date_, self.ticker_, result))
        dict_money[self.owner]['balances']['result'] += result
        if self.owner in dict_source and self.ticker_ in dict_source[self.owner]:
            pass
            #dict_source[self.owner][self.ticker_]['virt_wallet'] += result
        else:
            dict_source[self.owner][self.ticker_] = {'cash': 0.0, 'virt_wallet': result}

        ticker_cash = dict_source.get(self.owner, {}).get(self.ticker_, {}).get('cash', 0.0)
        ticker_virt = dict_source.get(self.owner, {}).get(self.ticker_, {}).get('virt_wallet', 0.0)
        ticker_mid = mid_sale
        print(f'ticker_virt {ticker_virt}, mid_sale {mid_sale}, ticker_cash {ticker_cash}, ticker_mid {ticker_mid}')
        if self.owner in dict_source and self.ticker_ in dict_source[self.owner]:
            if ticker_virt >= abs(mid_sale) and ticker_virt >= 0:
                dict_source[self.owner][self.ticker_]['virt_wallet'] -= mid_sale
                dict_money[self.owner]['virt_wallet'].append(
                    Money_in_out(self.date_, self.ticker_, mid_sale))
            else:
                ticker_diff = mid_sale - ticker_virt
                dict_source[self.owner][self.ticker_]['virt_wallet'] += ticker_virt
                dict_source[self.owner][self.ticker_]['cash'] -= ticker_diff
                dict_money[self.owner]['virt_wallet'].append(
                    Money_in_out(self.date_, self.ticker_, ticker_virt))
                dict_money[self.owner]['cash'].append(
                    Money_in_out(self.date_, self.ticker_, ticker_diff))
                print(
                    f' проверка ticker_virt {ticker_virt}, mid_sale {mid_sale}, ticker_cash {ticker_cash},'
                    f' ticker_mid {ticker_mid}, ticker_diff {ticker_diff}')

           #if mid_sale <= ticker_cash:
                #dict_source[self.owner][self.ticker_]['cash'] -= mid_sale
                #dict_money[self.owner]['cash'].append(
                #    Money_in_out(self.date_, self.ticker_, mid_sale))
                #dict_money[self.owner]['balances']['cash'] += mid_sale
            #else:
                # dict_source[self.owner][self.ticker_]['cash'] -= ticker_cash
                # dict_source[self.owner][self.ticker_]['virt_wallet'] -= mid_sale - ticker_cash
                # dict_money[self.owner]['cash'].append(
                #     Money_in_out(self.date_, self.ticker_, ticker_cash))
                # dict_money[self.owner]['balances']['virt_wallet'] += mid_sale - ticker_cash
        else:
                # Создаем вложенный словарь, если ключи отсутствуют
                dict_source[self.owner][self.ticker_] = {'cash': 0.0, 'virt_wallet': -mid_sale}
                dict_money[self.owner]['virt_wallet'].append(
                    Money_in_out(self.date_, self.ticker_, -mid_sale))
                dict_money[self.owner]['balances']['virt_wallet'] -= mid_sale
        print(f"продажи: по средней {mid_sale}, результат {result},"
              f" {dict_source.get(self.owner, {}).get(self.ticker_, {})}, {ticker_cash}")




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

    @property
    def report_type(self):
        return FINANCE_TYPE



class Comission(Selgitus):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        dict_saldo[self.firma_long].append(Moving(self.date_, 0, self.eursumm, self.owner))

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

    @property
    def report_type(self):
        return FINANCE_TYPE


class Something(Selgitus):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def report_type(self):
        eursumm = self.eursumm
        if eursumm > 0:
            return INPUT_TYPE
        else:
            return OUTPUT_TYPE


class Dividend_with_tax(Dividend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        category = 'div_with_tax'
        self.cash_flow(category)

    @property
    def report_type(self):
        return INPUT_TYPE


class Dividend_zero_tax(Dividend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        category = 'div_zero_tax'
        self.cash_flow(category)


    @property
    def report_type(self):
        return FINANCE_TYPE
