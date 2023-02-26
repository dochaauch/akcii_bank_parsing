from div_for_emta import read_file
from processing import create_pd

# Define constants
FIELDNAMES = ["cus_account", "string_type", "date_", "Receiver_payer", "description", "amount",
              "currency", "debit_credit", "archive_attribute", "trans_type", "ref_nr", "doc_nr", "emp"]

def main():
    target_file = '/Users/docha/Google Диск/akcii docha/2022/statement.csv'
    # target_file = '/Users/docha/Google Диск/akcii Tolika/2022/statement.csv'
    list_of_rows = read_file(target_file)
    df_full = create_pd(list_of_rows)
    print(df_full.to_string())


if __name__=="__main__":
    main()
