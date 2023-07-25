import unittest
from classes_for_statement import Buy_sell


class TestSellStocks(unittest.TestCase):

    def setUp(self):
        # Sample input data
        self.row_ = {
            'cus_account': 'EE272200221078511559',
            'string_type': '20',
            'date_': '11.07.2022',
            ' Receiver_payer': '',
            'description': 'SOBA-GY -150@20.92/SE:01V!4QAR0000AY000001 SWEDBANK',
            'amount': '3138,00',
            'currency': 'EUR',
            'debit_credit': 'K',
            'archive_attribute': '2022071100332827',
            'trans_type': 'M',
            'ref_nr': '',
            'doc_nr': '',
            'emp': ''
        }

        # Sample data for dict_money and dict_source
        self.dict_money = {
            'docha': {
                'result': [],
                'div_zero_tax': [],
                'div_with_tax': [],
                'cash': [],
                'virt_wallet': [],
                'balances': {
                    'result': 0,
                    'div_zero_tax': 0,
                    'div_with_tax': 0,
                    'cash': 0,  # You can set an initial cash balance
                    'virt_wallet': 0
                }
            }
        }

        self.dict_source = {
            'docha': {
                'SOBA-GY': {
                    'cash': 0,  # You can set an initial cash balance for this specific ticker
                    'virt_wallet': 0
                }
            }
        }

    def tearDown(self):
        # Sample data for dict_money and dict_source
        self.dict_money = {
            'docha': {
                'result': [],
                'div_zero_tax': [],
                'div_with_tax': [],
                'cash': [],
                'virt_wallet': [],
                'balances': {
                    'result': 0,
                    'div_zero_tax': 0,
                    'div_with_tax': 0,
                    'cash': 0,  # You can set an initial cash balance
                    'virt_wallet': 0
                }
            }
        }

        self.dict_source = {
            'docha': {
                'SOBA-GY': {
                    'cash': 0,  # You can set an initial cash balance for this specific ticker
                    'virt_wallet': 0
                }
            }
        }

    def test_sell_stocks_all_to_virt(self):
        # Create an instance of Buy_sell using the sample input data
        buy_sell_instance = Buy_sell(**self.row_)

        # Assert the changes made to dict_money and dict_source
        self.dict_money[buy_sell_instance.owner]['balances']['cash'] = 15000.00
        self.dict_source[buy_sell_instance.owner][buy_sell_instance.ticker_]['virt_wallet'] = 50

        print('***до', self.dict_source)
        print('***до', self.dict_money)
        # Call the sell_stocks method
        buy_sell_instance.sell_stocks(self.dict_money, self.dict_source)

        print('***после', self.dict_source)
        print('***после', self.dict_money)

        self.assertEqual(self.dict_money[buy_sell_instance.owner]['balances']['cash'], 6862.00)
        self.assertEqual(self.dict_source[buy_sell_instance.owner][buy_sell_instance.ticker_]['virt_wallet'], 3138)




if __name__ == '__main__':
    unittest.main()
