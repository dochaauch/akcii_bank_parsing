import collections

Share_data = collections.namedtuple('Share_data', 'full_name sanction')


ticker_dict = {'DAI': Share_data('Mercedes-Benz Group', 'no'),
               'PEP-GY': Share_data('PEPSICO INC GER', 'no'),
               'SPY5-GY': Share_data('SPDR S&P 500 UCITS ETF', 'no'),
               'O2D-GY': Share_data('Telefonica Deutschland', 'no'),
               'SOBA-GY': Share_data('AT&T INC GER', 'no'),
               'TVEAT': Share_data('TALLINNA VESI A-AKTSIA', 'no'),
               'VZ': Share_data('VERIZON COMMUNICATIONS INC', 'no'),
               'DOW-US': Share_data('DOW INC', 'no'),
               'MRK1T': Share_data('Merko Ehitus', 'no'),
               'TKM1T': Share_data('TALLINNA KAUBAMAJA GRUPP AKTSIA', 'no'),
               'POLY-LN': Share_data('POLYMETAL INTERNATIONAL PLC', 'yes'),
               'HRZN-US': Share_data('HORIZON TECHNOLOGY FINANCE CORP', 'no'),
               'EFC-US1': Share_data('ELLINGTON FINANCIAL INC', 'no'),
               'EARN-US': Share_data('ELLINGTON RESIDENTIAL MORTGAGE R', 'no'),
               'NLIS': Share_data('NOVOLIPETSK IRON AND STEEL (GDR)', 'yes'),
               'MAGNQ': Share_data('MAGNITOGORSK METALLURGICAL - GDR', 'yes'),
               'PHOR-LI': Share_data('PHOSAGRO PJSC GDR', 'yes'),
               'SEVERSTALGDR': Share_data('SEVERSTAL - GDR', 'yes'),
               'LKOD-LI': Share_data('LUKOIL SPON ADR LON', 'yes'),
               'PBR': Share_data('PETROLEO BRASILEIRO S.A.-ADR', 'no'),
               'ABR': Share_data('ARBOR REALTY TRUST INC', 'no'),
               'MNOD-LI1': Share_data('MMC NORILSK NICKEL PJSC ADR', 'yes'),
               'AB': Share_data('ALLIANCEBERNSTEIN HOLDING LP', 'no'),
               'GOGL-US1': Share_data('GOLDEN OCEAN GROUP LTD USA', 'no'),
               'ORC-US': Share_data('ORCHID ISLAND CAPITAL INC', 'no'),
               'ZIM-US': Share_data('ZIM INTEGRATED SHIPPING SERVICE', 'no'),
               }




#for key in sorted(ticker_dict):
#    print(key, ticker_dict[key])