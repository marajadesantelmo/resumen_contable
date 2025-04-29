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
    
    # This is a placeholder for the "Histórico" page
    # It will display historical data with options to select date ranges
    
    st.info("En esta sección se mostrará la información histórica de períodos anteriores.")
    st.write("Esta sección está en desarrollo y pronto estará disponible.")
    
    # Example placeholder for date range selection
    col1, col2 = st.columns(2)
    with col1:
        st.date_input("Fecha de inicio", value=None)
    with col2:
        st.date_input("Fecha de fin", value=None)
    
    # Placeholder for company selection
    st.selectbox("Seleccionar Empresa", options=["Todas las empresas"])
    
    # Example placeholder for historical data visualization
    st.header("Evolución Histórica")
    st.write("Aquí se mostrarán gráficos de evolución de los principales indicadores a lo largo del tiempo.")
    
    # Example tabs for different historical views
    tab1, tab2, tab3 = st.tabs(["Resumen Mensual", "Comparativa Interanual", "Tendencias"])
    
    with tab1:
        st.write("Vista de resúmenes mensuales")
    with tab2:
        st.write("Comparativa entre períodos similares de diferentes años")
    with tab3:
        st.write("Análisis de tendencias")
