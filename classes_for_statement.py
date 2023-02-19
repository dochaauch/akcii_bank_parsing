from collections import namedtuple
from collections import defaultdict
from datetime import datetime, date
from currency_converter import CurrencyConverter
import re
import ticker_dict

c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_wrong_date=True)
dict_shares = defaultdict(list)
Moving = namedtuple('Moving', 'date_ qnt amount owner')

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