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
    ventas_por_empresa_cliente = pd.read_csv('data/ventas_historico_cliente.csv')
    compras_por_empresa_proveedor = pd.read_csv('data/compras_historico_proveedor.csv')

    # Filter data based on username
    comprobantes_historicos = filter_restricted_data(comprobantes_historicos, username)
    ventas_por_empresa_cliente = filter_restricted_data(ventas_por_empresa_cliente, username)
    compras_por_empresa_proveedor = filter_restricted_data(compras_por_empresa_proveedor, username)

    # Date range selection
    st.info("Datos Históricos en base a Comprobantes de ARCA")

    # Display datasets
    st.header("Evolución Histórica")
    tab1, tab2, tab3, tab4 = st.tabs(["Ventas y Compras", "IVA", "Clientes", "Proveedores"])

    with tab1:
        st.subheader("Ventas y Compras")


        selected_razon_social = st.selectbox(
            "Seleccione Razón Social", 
            comprobantes_historicos['Razon Social'].unique(), 
            key="ventas_compras_selectbox"
        )

        filtered_data = comprobantes_historicos[comprobantes_historicos['Razon Social'] == selected_razon_social]
        if not filtered_data.empty:         
            chart = alt.Chart(filtered_data).mark_bar().encode(
                x='Mes:T',
                y=alt.Y('Neto Compras:Q', title='Neto Compras'),
                color=alt.value('steelblue')
            ).properties(
                width=600,
                height=400
            ) + alt.Chart(filtered_data).mark_bar().encode(
                x='Mes:T',
                y=alt.Y('Neto Ventas:Q', title='Neto Ventas'),
                color=alt.value('orange')
            )

            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para la Razón Social seleccionada.")
        st.dataframe(comprobantes_historicos)

    with tab2:
        st.subheader("IVA")
        st.dataframe(comprobantes_historicos[['Razon Social', 'Mes', 'IVA Ventas', 'IVA Compras', 'Saldo IVA']])
        selected_razon_social = st.selectbox(
            "Seleccione Razón Social", 
            comprobantes_historicos['Razon Social'].unique(), 
            key="iva_selectbox"
        )
        filtered_data = comprobantes_historicos[comprobantes_historicos['Razon Social'] == selected_razon_social]
        
        if not filtered_data.empty:
            filtered_data['Mes'] = pd.to_datetime(filtered_data['Mes'], format='%Y-%m')
            st.bar_chart(
                filtered_data.set_index('Mes')[['IVA Ventas', 'IVA Compras', 'Saldo IVA']],
                use_container_width=True,
                height=400
            )
        else:
            st.warning("No hay datos disponibles para la Razón Social seleccionada.")
    with tab3:
        st.subheader("Ventas por cliente")
        st.dataframe(ventas_por_empresa_cliente)
        st.bar_chart(ventas_por_empresa_cliente.groupby('Empresa')[['Neto', 'IVA']].sum())

    with tab4:
        st.subheader("Compras por proveedor")
        st.dataframe(compras_por_empresa_proveedor)
        st.bar_chart(compras_por_empresa_proveedor.groupby('Empresa')[['Neto', 'IVA']].sum())
