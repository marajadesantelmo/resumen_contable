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
    comprobantes_por_empresa = pd.read_csv('data/comprobantes_historicos.csv')
    ventas_por_empresa_cliente = pd.read_csv('data/ventas_historico_cliente.csv')
    compras_por_empresa_proveedor = pd.read_csv('data/compras_historico_proveedor.csv')

    # Filter data based on username
    comprobantes_por_empresa = filter_restricted_data(comprobantes_por_empresa, username)
    ventas_por_empresa_cliente = filter_restricted_data(ventas_por_empresa_cliente, username)
    compras_por_empresa_proveedor = filter_restricted_data(compras_por_empresa_proveedor, username)

    # Date range selection
    st.info("Datos Históricos en base a Comprobantes de ARCA")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha de inicio", value=None)
    with col2:
        end_date = st.date_input("Fecha de fin", value=None)

    # Filter datasets by date range if selected
    if start_date and end_date:
        comprobantes_por_empresa = comprobantes_por_empresa[
            (pd.to_datetime(comprobantes_por_empresa['Fecha de Emisión'], format='%d/%m/%Y') >= start_date) &
            (pd.to_datetime(comprobantes_por_empresa['Fecha de Emisión'], format='%d/%m/%Y') <= end_date)
        ]
        ventas_por_empresa_cliente = ventas_por_empresa_cliente[
            (pd.to_datetime(ventas_por_empresa_cliente['Mes'], format='%m-%Y') >= start_date) &
            (pd.to_datetime(ventas_por_empresa_cliente['Mes'], format='%m-%Y') <= end_date)
        ]
        compras_por_empresa_proveedor = compras_por_empresa_proveedor[
            (pd.to_datetime(compras_por_empresa_proveedor['Mes'], format='%m-%Y') >= start_date) &
            (pd.to_datetime(compras_por_empresa_proveedor['Mes'], format='%m-%Y') <= end_date)
        ]

    # Display datasets
    st.header("Evolución Histórica")
    tab1, tab2, tab3 = st.tabs(["Ventas y Compras", "Clientes", "Proveedores"])

    with tab1:
        st.subheader("Ventas y Compras")
        st.dataframe(comprobantes_por_empresa)
        selected_razon_social = st.selectbox("Seleccione Razón Social", comprobantes_por_empresa['Razon Social'].unique())
        filtered_data = comprobantes_por_empresa[comprobantes_por_empresa['Razon Social'] == selected_razon_social]
        
        if not filtered_data.empty:
            filtered_data['Mes'] = pd.to_datetime(filtered_data['Mes'], format='%m-%Y')
            numeric_columns = filtered_data.select_dtypes(include='number').columns
            
            st.line_chart(
            filtered_data.set_index('Mes')[numeric_columns],
            use_container_width=True
            )
        else:
            st.warning("No hay datos disponibles para la Razón Social seleccionada.")

    with tab2:
        st.subheader("Ventas por cliente")
        st.dataframe(ventas_por_empresa_cliente)
        st.bar_chart(ventas_por_empresa_cliente.groupby('Cliente')['Importe Total'].sum())

    with tab3:
        st.subheader("Compras por proveedor")
        st.dataframe(compras_por_empresa_proveedor)
        st.bar_chart(compras_por_empresa_proveedor.groupby('Proveedor')['Importe Total'].sum())
