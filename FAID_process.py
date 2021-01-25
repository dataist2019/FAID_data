import pandas as pd
import streamlit as st
import datetime
import re
import base64
import pathlib

st.title('FAID Data')

st.markdown("""
This app allows users to easily download FAID data to respond to data calls
FAID uses FAE data and improves it by applying business rules identified by F stakeholders
""")

st. write("""
## Customize your selection
Using the sidebar menu you can select *Fiscal Year*, *Transaction Type* and *Bureau*

* **Fiscal Year:** Pick the time period for the export
* **Transaction Type:** Select Obligations and/or Disbursements
* **Bureau:** Choose one or more bureaus
""")



st.sidebar.header('User Input Features')
#selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950,2020))))

@st.cache
def load_data(file):
    df = pd.read_excel(file)
    df['Fiscal Year'] = pd.to_numeric(df['Fiscal Year'], errors='coerce')
    df = df[df['Fiscal Year']>2010]
    return df

file = 'Financial_Data_12012020.xlsx'
clean_table = load_data(file)

# Sidebar - Team selection
sorted_unique_tt = sorted(clean_table['Transaction Type'].unique())
selected_transaction = st.sidebar.multiselect('Transaction Type', sorted_unique_tt, sorted_unique_tt)

# Filtering data
df_filtered = clean_table[(clean_table['Transaction Type'].isin(selected_transaction)) ]

slider_1, slider_2 = st.sidebar.slider(
'Select a range of values', df_filtered['Fiscal Year'].min(), df_filtered['Fiscal Year'].max(), (df_filtered['Fiscal Year'].min(), df_filtered['Fiscal Year'].max()))
filtered_df = df_filtered.loc[(df_filtered["Fiscal Year"] >= slider_1) & (df_filtered['Fiscal Year']<=slider_2),:]

# Sidebar - Team selection
sorted_unique_bureau = sorted(filtered_df['Bureau'].unique())
selected_transaction_2 = st.sidebar.multiselect('Bureau', sorted_unique_bureau, sorted_unique_bureau)

# Filtering data
filtered_df_final = filtered_df[(filtered_df['Bureau'].isin(selected_transaction_2)) ]


st.header('FAID Table')
st.write('Data Dimension: ' + str(filtered_df_final.shape[0]) + ' rows and ' + str(filtered_df_final.shape[1]) + ' columns.')
#st.dataframe(filtered_df_final)
#st.table(filtered_df_final)

# HACK This only works when we've installed streamlit with pipenv, so the
# permissions during install are the same as the running process
STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / 'static'
# We create a downloads directory within the streamlit static asset directory
# and we write output files to it
DOWNLOADS_PATH = (STREAMLIT_STATIC_PATH / "downloads")
if not DOWNLOADS_PATH.is_dir():
    DOWNLOADS_PATH.mkdir()

def main():
    st.markdown("Download from [downloads/mydata.csv](downloads/mydata.csv)")
    filtered_df_final.to_csv(str(DOWNLOADS_PATH / "mydata.csv"), index=False)

if __name__ == "__main__":
    main()


#def filedownload(df):
    #We csv = df.to_csv(index=False)
    #b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    #href = <a href="data:file/csv;TREAMLIT_STATIC_PATH/downloads download="mydata.csv">Download CSV File</a>'
    #return href

#st.markdown(filedownload(filtered_df_final), unsafe_allow_html=True)

filtered_df_final['FY'] = pd.to_datetime(filtered_df_final['Fiscal Year'])

#st.line_chart(filtered_df_final.Amount)
#‎st.markdown("Download from [downloads/mydata.csv](downloads/mydata.csv)")
#mydataframe.to_csv(str(DOWNLOADS_PATH / "mydata.csv"), index=False)
