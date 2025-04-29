import streamlit as st
import pandas as pd
from io import BytesIO

def format_currency(x):
    """Format number as Argentine peso currency"""
    return f"${x:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".") if x >= 0 else f"(${abs(x):,.0f})".replace(",", "X").replace(".", ",").replace("X", ".")

def filter_restricted_data(df, username):
    """Filter out restricted data based on username"""
    if username != "FU":
        return df
    
    # Companies to filter out for FU
    restricted_companies = ["BA Comex", "De la Arena Coll Manuel", "Winehaus", "Nerococina"]
    
    if 'razon_social' in df.columns:
        return df[~df['razon_social'].isin(restricted_companies)]
    elif 'Sociedad' in df.columns:
        return df[~df['Sociedad'].isin(restricted_companies)]
    
    return df


def fetch_data(): 
    resumen_contable_mes_actual = pd.read_csv('data/resumen_contable_mes_actual.csv')
    resumen_contable_mes_actual_excel = resumen_contable_mes_actual.copy()
    for column in resumen_contable_mes_actual.columns:
        if column != 'Sociedad':
            resumen_contable_mes_actual[column] = resumen_contable_mes_actual[column].apply(format_currency)
    with open('data/leyenda_resumen_contable_mes_actual.txt', 'r', encoding='utf-8') as file:
        leyenda = file.read()
    return resumen_contable_mes_actual, resumen_contable_mes_actual_excel, leyenda

def show_page(username):
    resumen_contable_mes_actual, resumen_contable_mes_actual_excel, leyenda = fetch_data()
    st.title(leyenda)
    st.dataframe(resumen_contable_mes_actual, use_container_width=True, hide_index=True)
    st.download_button(
        label="Descargar Resumen Contable (Excel)",
        data=resumen_contable_mes_actual_excel.to_excel(index=False).encode('utf-8'),
        file_name='Resumen_Contable_Mes_Actual.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Emitidos del Mes Corriente")
        st.write("Aquí se mostrarán los comprobantes emitidos del mes en curso.")
    with col2:
        st.subheader("Recibidos del Mes Corriente")
        st.write("Aquí se mostrarán los comprobantes recibidos del mes en curso.")
