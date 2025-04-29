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
    st.title("Resumen Contable - Mes Corriente (Abril 2025)")
    
    # This is a placeholder for the "Mes Corriente" page
    # It will have similar structure as the "Resumen Mes Vencido" page
    # but will use different data sources
    
    st.info("En esta sección se mostrará la información del mes en curso.")
    st.write("Esta sección está en desarrollo y pronto estará disponible.")
    
    # You can add placeholder widgets to show the intended structure
    st.header("Vista Previa - Comprobantes del Mes en Curso")
    
    # Example placeholder for data that would be shown
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Emitidos del Mes Corriente")
        st.write("Aquí se mostrarán los comprobantes emitidos del mes en curso.")
    with col2:
        st.subheader("Recibidos del Mes Corriente")
        st.write("Aquí se mostrarán los comprobantes recibidos del mes en curso.")
