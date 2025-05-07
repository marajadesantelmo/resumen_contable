import streamlit as st
import pandas as pd
from io import BytesIO
import altair as alt

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

def show_page(username):
    st.title("Resumen Contable - Histórico")
    
    # Load datasets
    comprobantes_historicos = pd.read_csv('data/comprobantes_historicos.csv')

    # Filter data based on username
    comprobantes_historicos = filter_restricted_data(comprobantes_historicos, username)

    # Date range selection
    st.info("Datos Históricos en base a Comprobantes de ARCA")

    # Display datasets
    st.header("Evolución Histórica")
    tab1, tab2, tab3, tab4 = st.tabs(["Ventas y Compras", "IVA"])

    with tab1:
        st.subheader("Ventas y Compras")
        selected_razon_social = st.selectbox(
            "Seleccione Razón Social", 
            comprobantes_historicos['Razon Social'].unique(), 
            key="ventas_compras_selectbox"
        )
        filtered_data = comprobantes_historicos[(comprobantes_historicos['Razon Social'] == selected_razon_social) &
                                                (comprobantes_historicos['Variable'].isin(['Neto Ventas', 'Neto Compras']))]
        if not filtered_data.empty:         
           st.bar_chart(filtered_data, x="Mes", y="Monto", color="Variable", stack=False)
        else:
            st.warning("No hay datos disponibles para la Razón Social seleccionada.")
        st.dataframe(comprobantes_historicos)

    with tab2:

        st.subheader("IVA")
        selected_razon_social = st.selectbox(
            "Seleccione Razón Social", 
            comprobantes_historicos['Razon Social'].unique(), 
            key="iva_selectbox"
        )
        filtered_data = comprobantes_historicos[(comprobantes_historicos['Razon Social'] == selected_razon_social) &
                                                (comprobantes_historicos['Variable'].isin(['IVA Ventas', 'IVA Compras', 'Saldo IVA']))]
        if not filtered_data.empty:         
           st.bar_chart(filtered_data, x="Mes", y="Monto", color="Variable", stack=False)
        else:
            st.warning("No hay datos disponibles para la Razón Social seleccionada.")
        st.dataframe(comprobantes_historicos)