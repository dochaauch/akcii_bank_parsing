#https://www.reddit.com/r/learnpython/comments/iwciyk/how_to_display_subtotals_for_columns_using_pandas/

import pandas as pd
lst1 = [1,2,3,4,5,6,7,8,9,10,11,12]
lst2 = ['APAC', 'APAC', 'EUROPE', 'EUROPE', 'EUROPE', 'EUROPE', 'EUROPE', 'EUROPE', 'EUROPE', 'EUROPE',
        'EUROPE', 'USA']
lst3 = ['HK', 'HK', 'UK', 'UK', 'UK', 'UK', 'UK', 'UK', 'IT', 'FR', 'FR', 'CALI']
lst4 = ['SG', 'SG', 'SG', 'SG', 'SG', 'SG', 'SG', 'SG', 'SG', 'SG', 'SG', 'AU']
lst5 = ['Y', 'Y', 'N', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y']
df = pd.DataFrame(list(zip(lst1, lst2, lst3, lst4, lst5)),
               columns =['ID', 'Division', 'District', 'Destination', 'OnTime'])

print(df.to_string())

# Create the pivot_table. Set margins=False (totals added in the end)
pvt = df.pivot_table(index=['Division','District'],
                    columns=['Destination','OnTime'],
                    margins = False,  aggfunc='count', fill_value=0)

print(pvt.to_string())

# subtotal of the rows
subtotal_rows=pvt.groupby(level=0).sum()
print(subtotal_rows)

# rename the index in order to concatenate  with pvt
subtotal_rows.index=pd.MultiIndex.from_arrays([subtotal_rows.index, len(subtotal_rows.index) * ['subtotal']])
print(subtotal_rows.index)

# add the subtotals rows to pvt
pvt=pd.concat([pvt,subtotal_rows]).sort_index()
print(pvt.to_string())

# subtotal of the columns
subtotal_cols=pvt.groupby(level=1,axis=1).sum()
print(subtotal_cols)

# rename the columns in order to join with pvt
subtotal_cols.columns=pd.MultiIndex.from_arrays([len(subtotal_cols.columns)*["ID"],subtotal_cols.columns, len(subtotal_cols.columns) * ['subtotal']])
print(subtotal_cols.columns)

# add the subtotals columns to pvt
pvt=pvt.join(subtotal_cols).sort_index(axis=1)
print(pvt)

# Add the totals of the columns and rows
# Divide by 2 because we are summing the subtotals rows and columns too
pvt.loc[("Total",""),:]=pvt.sum()/2
pvt.loc[:,("ID","Total","")]=pvt.sum(axis=1)/2

print(pvt)

