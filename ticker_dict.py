import collections

#если тикер не добавлен в словарь, то файл main выдаст ошибку при присвоении класса
#KeyError: 'ARR-US'
#если ввести ключ дважды, он подсветится


Share_data = collections.namedtuple('Share_data', 'full_name sanction country reg_nr',)


ticker_dict = {'DAI': Share_data('Mercedes-Benz Group', 'no', 'Германия', '',),
               'PEP-GY': Share_data('PEPSICO INC GER', 'no', 'Соединенные Штаты Америки', 'US7134481081',),
               'SPY5-GY': Share_data('SPDR S&P 500 UCITS ETF', 'no', 'Ирландия', 'IE00B6YX5C33',),
               'O2D-GY': Share_data('Telefonica Deutschland', 'no', '', '',),
               'SOBA-GY': Share_data('AT&T INC GER', 'no', 'Соединенные Штаты Америки', 'US00206R1023',),
               'TVEAT': Share_data('TALLINNA VESI A-AKTSIA', 'no', 'Эстония', 'EE3100026436',),
               'VZ': Share_data('VERIZON COMMUNICATIONS INC', 'no', 'Соединенные Штаты Америки', 'US92343V1044',),
               'DOW-US': Share_data('DOW INC', 'no', 'Соединенные Штаты Америки', 'US2605571031',),
               'MRK1T': Share_data('Merko Ehitus', 'no', '', '',),
               'TKM1T': Share_data('TALLINNA KAUBAMAJA GRUPP AKTSIA', 'no', 'Эстония', 'EE0000001105',),
               'POLY-LN': Share_data('POLYMETAL INTERNATIONAL PLC', 'yes', '', '',),
               'HRZN-US': Share_data('HORIZON TECHNOLOGY FINANCE CORP', 'no', 'Соединенные Штаты Америки', 'US44045A1025',),
               'EFC-US1': Share_data('ELLINGTON FINANCIAL INC', 'no', 'Соединенные Штаты Америки', 'US28852N1090',),
               'EARN-US': Share_data('ELLINGTON RESIDENTIAL MORTGAGE R', 'no', 'Соединенные Штаты Америки', 'US2885781078',),
               'NLIS': Share_data('NOVOLIPETSK IRON AND STEEL (GDR)', 'yes', '', '',),
               'MAGNQ': Share_data('MAGNITOGORSK METALLURGICAL - GDR', 'yes', '', '',),
               'PHOR-LI': Share_data('PHOSAGRO PJSC GDR', 'yes', '', '',),
               'SEVERSTALGDR': Share_data('SEVERSTAL - GDR', 'yes', '', '',),
               'LKOD-LI': Share_data('LUKOIL SPON ADR LON', 'yes', '', '',),
               'PBR': Share_data('PETROLEO BRASILEIRO S.A.-ADR', 'no', 'Соединенные Штаты Америки', 'US71654V4086',),
               'ABR': Share_data('ARBOR REALTY TRUST INC', 'no', 'Соединенные Штаты Америки', 'US0389231087',),
               'MNOD-LI1': Share_data('MMC NORILSK NICKEL PJSC ADR', 'yes', '', '',),
               'AB': Share_data('ALLIANCEBERNSTEIN HOLDING LP', 'no', '', '',),
               'GOGL-US1': Share_data('GOLDEN OCEAN GROUP LTD USA', 'no', 'Багамские острова', 'BMG396372051',),
               'ORC-US': Share_data('ORCHID ISLAND CAPITAL INC', 'no', 'Соединенные Штаты Америки', 'US68571X1037',),
               'ZIM-US': Share_data('ZIM INTEGRATED SHIPPING SERVICE', 'no', 'Израиль', 'IL0065100930',),
               'J5A-GR': Share_data('Warner Bros Discovery Inc', 'no', '', '',),
               'ARR-US': Share_data('ARMOUR RESIDENTIAL REIT INC', 'no', 'Соединенные Штаты Америки', 'US0423155078',),

               }




#for key in sorted(ticker_dict):
#    print(key, ticker_dict[key])