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

    comprobantes_historicos = pd.read_csv('data/comprobantes_historicos.csv')
    comprobantes_historicos = filter_restricted_data(comprobantes_historicos, username)

    ventas_por_empresa_cliente = pd.read_csv('data/ventas_historico_cliente.csv')
    ventas_por_empresa_cliente = filter_restricted_data(ventas_por_empresa_cliente, username)

    compras_por_empresa_proveedor = pd.read_csv('data/compras_historico_proveedor.csv')
    compras_por_empresa_proveedor = filter_restricted_data(compras_por_empresa_proveedor, username)

    st.info("Datos Históricos en base a Comprobantes de ARCA")
    tab1, tab2, tab3 = st.tabs(["Ventas y Compras", "IVA", "Clientes"])
    with tab1:
        tab1_col1, tab1_col2 = st.columns([2, 1])
        with tab1_col1:
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
        with tab1_col2:
            # Pivot the data to have columns Mes, Neto Ventas, and Neto Compras
            pivoted_data = filtered_data.pivot(index="Mes", columns="Variable", values="Monto").reset_index()
            for column in [ "Neto Ventas", "Neto Compras"]:
                pivoted_data[column] = pivoted_data[column].apply(format_currency)
            st.dataframe(pivoted_data, hide_index=True)

    with tab2:
        tab2_col1, tab2_col2 = st.columns([2, 1])
        with tab2_col1:
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
        with tab2_col2:
            # Pivot the data to have columns Mes, IVA Ventas, IVA Compras, and Saldo IVA
            pivoted_data = filtered_data.pivot(index="Mes", columns="Variable", values="Monto").reset_index()
            pivoted_data = pivoted_data[["Mes", "IVA Ventas", "IVA Compras", "Saldo IVA"]]
            for column in [ "IVA Ventas", "IVA Compras", "Saldo IVA"]:
                pivoted_data[column] = pivoted_data[column].apply(format_currency)
            st.dataframe(pivoted_data, hide_index=True)

    with tab3:
        st.subheader("Clientes")
        selected_razon_social = st.selectbox(
            "Seleccione Razón Social", 
            ventas_por_empresa_cliente['Razon Social'].unique(), 
            key="clientes_selectbox"
        )

        filtered_data = ventas_por_empresa_cliente[(ventas_por_empresa_cliente['Razon Social'] == selected_razon_social)]
        pivoted_data_clientes = filtered_data.groupby(["Empresa", "Mes"]).agg({"Neto": "sum"}).reset_index()
        pivoted_data_clientes = pivoted_data_clientes.pivot(index="Empresa", columns="Mes", values="Neto").reset_index()
        pivoted_data.fillna(0, inplace=True)
        pivoted_data_clientes.iloc[:, 1:] = pivoted_data_clientes.iloc[:, 1:].round(0).astype(int)
        # Add a total column and sort by it
        pivoted_data_clientes["Total"] = pivoted_data_clientes.iloc[:, 1:].sum(axis=1)
        pivoted_data_clientes.sort_values(by="Total", ascending=False, inplace=True)
        for column in pivoted_data_clientes.columns[1:]:
            pivoted_data_clientes[column] = pivoted_data_clientes[column].apply(format_currency)
        st.dataframe(pivoted_data_clientes, hide_index=True)
        if not filtered_data.empty:   
                st.header("Evolución del top 10 Clientes")      
                st.bar_chart(pivoted_data_clientes.head(10), x="Mes", y="Total", color="Empresa", stack=False)
        else:
            st.warning("No hay datos disponibles para la Razón Social seleccionada.")
        # Pivot the data to have columns Mes and Clientes
