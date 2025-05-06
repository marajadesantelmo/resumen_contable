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

def show_page(username):
    st.title("Resumen Contable - Histórico")
    
    # Load datasets
    emitidos_historico = pd.read_csv('data/historico_procesado/emitidos_historico.csv')
    recibidos_historico = pd.read_csv('data/historico_procesado/recibidos_historico.csv')
    ventas_por_empresa = pd.read_csv('data/ventas_historico_mensual.csv')
    compras_por_empresa = pd.read_csv('data/compras_historico_mensual.csv')
    ventas_por_empresa_cliente = pd.read_csv('data/ventas_historico_cliente.csv')
    compras_por_empresa_proveedor = pd.read_csv('data/compras_historico_proveedor.csv')

    # Filter data based on username
    emitidos_historico = filter_restricted_data(emitidos_historico, username)
    recibidos_historico = filter_restricted_data(recibidos_historico, username)
    ventas_por_empresa = filter_restricted_data(ventas_por_empresa, username)
    compras_por_empresa = filter_restricted_data(compras_por_empresa, username)
    ventas_por_empresa_cliente = filter_restricted_data(ventas_por_empresa_cliente, username)
    compras_por_empresa_proveedor = filter_restricted_data(compras_por_empresa_proveedor, username)

    # Date range selection
    st.info("En esta sección se mostrará la información histórica de períodos anteriores.")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha de inicio", value=None)
    with col2:
        end_date = st.date_input("Fecha de fin", value=None)

    # Filter datasets by date range if selected
    if start_date and end_date:
        emitidos_historico = emitidos_historico[
            (pd.to_datetime(emitidos_historico['Fecha de Emisión']) >= start_date) &
            (pd.to_datetime(emitidos_historico['Fecha de Emisión']) <= end_date)
        ]
        recibidos_historico = recibidos_historico[
            (pd.to_datetime(recibidos_historico['Fecha de Emisión']) >= start_date) &
            (pd.to_datetime(recibidos_historico['Fecha de Emisión']) <= end_date)
        ]
        ventas_por_empresa = ventas_por_empresa[
            (pd.to_datetime(ventas_por_empresa['Mes'], format='%m-%Y') >= start_date) &
            (pd.to_datetime(ventas_por_empresa['Mes'], format='%m-%Y') <= end_date)
        ]
        compras_por_empresa = compras_por_empresa[
            (pd.to_datetime(compras_por_empresa['Mes'], format='%m-%Y') >= start_date) &
            (pd.to_datetime(compras_por_empresa['Mes'], format='%m-%Y') <= end_date)
        ]

    # Display datasets
    st.header("Evolución Histórica")
    tab1, tab2, tab3 = st.tabs(["Emitidos y Recibidos", "Ventas y Compras", "Clientes y Proveedores"])

    with tab1:
        st.subheader("Emitidos Histórico")
        st.dataframe(emitidos_historico)
        st.subheader("Recibidos Histórico")
        st.dataframe(recibidos_historico)

    with tab2:
        st.subheader("Ventas por Empresa")
        st.dataframe(ventas_por_empresa)
        st.subheader("Compras por Empresa")
        st.dataframe(compras_por_empresa)

    with tab3:
        st.subheader("Ventas por Empresa y Cliente")
        st.dataframe(ventas_por_empresa_cliente)
        st.subheader("Compras por Empresa y Proveedor")
        st.dataframe(compras_por_empresa_proveedor)
