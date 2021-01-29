import pandas as pd
import streamlit as st
import datetime
import re
import base64
import pathlib
import altair as alt

st.set_page_config(
    page_title="FAID Download Portal",
    layout='wide',
    initial_sidebar_state='auto',
)

t1, t2 = st.beta_columns(2)
with t1:
    st.markdown('# FAID Data')

with t2:
    st.write("")
    st.write("")
    st.write("""
    **Guidehouse** | National Security Segment | FA.gov/FADR Team
    """)

#st.title('FAID Data')
st.write('')
st.write("")
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
'Select Fiscal Years', df_filtered['Fiscal Year'].min(), df_filtered['Fiscal Year'].max(), (df_filtered['Fiscal Year'].min(), df_filtered['Fiscal Year'].max()))
filtered_df = df_filtered.loc[(df_filtered["Fiscal Year"] >= slider_1) & (df_filtered['Fiscal Year']<=slider_2),:]

# Sidebar - Team selection
sorted_unique_bureau = sorted(filtered_df['Bureau'].unique())
selected_transaction_2 = st.sidebar.multiselect('Bureau', sorted_unique_bureau, sorted_unique_bureau)

# Filtering data
filtered_df_final = filtered_df[(filtered_df['Bureau'].isin(selected_transaction_2)) ]


st.write("""
## Summary results
Please use the table and chart below to review results and corroborate the data is accurate

""")
st.write('*Data Dimension: ' + str(filtered_df_final.shape[0]) + ' rows and ' + str(filtered_df_final.shape[1]) + ' columns.*')
#st.dataframe(filtered_df_final)
#st.table(filtered_df_final)


filtered_df_final['FY'] = pd.to_datetime(filtered_df_final['Fiscal Year'])

new_df = filtered_df_final.groupby(['Fiscal Year', 'Transaction Type'])['Amount'].sum()
new_df = new_df.reset_index()
new_df = pd.DataFrame(new_df)
df_pivot = new_df.pivot(values='Amount', index='Fiscal Year', columns='Transaction Type')
#st.dataframe(new_df)

q1, q2 = st.beta_columns((1,2))
with q1:
    st.write('**Table**')
    st.table(df_pivot)

with q2:
    st.write('**Bar Chart**')
    alt.themes.enable("ggplot2")
    range_ = ['#fd9714','steelblue']
    p = alt.Chart(new_df).mark_bar().encode(alt.X('Transaction Type:N', title=''), alt.Y('Amount:Q', title='Amount in $'), alt.Color('Transaction Type:N', scale=alt.Scale(range=range_)), alt.Column('Fiscal Year:O', title=''), tooltip = ['Transaction Type', 'Fiscal Year', 'Amount']).properties(width=alt.Step(30)).configure_axis(
    grid=False
).configure_view(
    strokeWidth=0
)
    st.altair_chart(p, use_container_width=False)
#st.table(df_pivot)
#st.bar_chart(new_df)
#alt.themes.enable("ggplot2")
#p = alt.Chart(new_df).mark_bar().encode(alt.X('Transaction Type:N', title=''), alt.Y('Amount:Q', title='Amount in $'), alt.Color('Transaction Type:N'), alt.Column('Fiscal Year:O')).properties(width=alt.Step(60))
#st.altair_chart(p, use_container_width=False)
#st.write(p, use_container_width=True)
#st.line_chart(filtered_df_final.Amount)

with st.sidebar.beta_expander("Click to learn more about the data source"):
    st.markdown("""
    FAE data includes a few Treasury Accounts that F does not consider related to foreign assistance. Thus, FAID does not include the following accounts: *Foreign National Employees Separation*, *The White House*, and *Diplomatic and Consular*

    The F-DATA Team used a country/operating unit crosswalk to modify country names and match DOS country convention. The same crosswalk was used to add a *Bureau* column.

    Click here to review additional documentation for **[FAE](https://explorer.usaid.gov/data)**
    """)

# HACK This only works when we've installed streamlit with pipenv, so the
# permissions during install are the same as the running process
STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / 'static'
# We create a downloads directory within the streamlit static asset directory
# and we write output files to it
DOWNLOADS_PATH = (STREAMLIT_STATIC_PATH / "downloads")
if not DOWNLOADS_PATH.is_dir():
    DOWNLOADS_PATH.mkdir()


#def main():
    st.markdown('## Download option')
    st.markdown("### Once you completed your selection you can download the data [here](downloads/mydata.csv)")
    filtered_df_final.to_csv(str(DOWNLOADS_PATH / "mydata.csv"), index=False)

#if __name__ == "__main__":
    main()


#def filedownload(df):
    #We csv = df.to_csv(index=False)
    #b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    #href = <a href="data:file/csv;TREAMLIT_STATIC_PATH/downloads download="mydata.csv">Download CSV File</a>'
    #return href

#st.markdown(filedownload(filtered_df_final), unsafe_allow_html=True)

csv = filtered_df_final.to_csv(index=False)
b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
href = f'<a href="data:file/csv;base64,{b64}">Download Data as CSV File</a>'
st.markdown(href, unsafe_allow_html=True)
