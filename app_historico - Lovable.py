import streamlit as st
import pandas as pd
from io import BytesIO
import altair as alt
from supabase_connection import fetch_table_data

def fetch_data(username):
    comprobantes_historicos = fetch_table_data('comprobantes_historicos')
    emitidos_historicos = fetch_table_data('emitidos_historico')
    recibidos_historicos = fetch_table_data('recibidos_historico')
    ventas_por_empresa_cliente = fetch_table_data('ventas_historico_cliente')
    compras_por_empresa_proveedor = fetch_table_data('compras_historico_proveedor')
    clientes_activos = fetch_table_data('clientes_activos')
    return (comprobantes_historicos, emitidos_historicos, recibidos_historicos, ventas_por_empresa_cliente, compras_por_empresa_proveedor, clientes_activos)

def show_page(username):
    comprobantes_historicos, emitidos_historicos, recibidos_historicos, ventas_por_empresa_cliente, compras_por_empresa_proveedor, clientes_activos = fetch_data(username)
    st.title("Resumen Contable - Histórico")
    st.info("Datos Históricos en base a Comprobantes de ARCA")

    # Selectbox for "Razón Social" outside the tabs
    selected_razon_social = st.selectbox(
        "Seleccione Razón Social",
        comprobantes_historicos['Razon Social'].unique(),
        key="razon_social_selectbox"
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Ventas y Compras", "IVA", "Clientes", "Proveedores", "Clientes Activos/Perdidos"])
    with tab1:
        tab1_col1, tab1_col2 = st.columns([2, 1])
        with tab1_col1:
            st.subheader("Ventas y Compras")
            filtered_data = comprobantes_historicos[
                (comprobantes_historicos['Razon Social'] == selected_razon_social) &
                (comprobantes_historicos['Variable'].isin(['Neto Ventas', 'Neto Compras']))
            ]
            if not filtered_data.empty:
                st.bar_chart(filtered_data, x="Mes", y="Monto", color="Variable", stack=False)
            else:
                st.warning("No hay datos disponibles para la Razón Social seleccionada.")
        with tab1_col2:
            # Pivot the data to have columns Mes, Neto Ventas, and Neto Compras
            pivoted_data_ventas_compras = filtered_data.pivot(index="Mes", columns="Variable", values="Monto").reset_index()
            pivoted_data_ventas_compras = pivoted_data_ventas_compras[["Mes", "Neto Ventas", "Neto Compras"]]
            pivoted_data_ventas_compras['Dif.'] = pivoted_data_ventas_compras['Neto Ventas'] - pivoted_data_ventas_compras['Neto Compras']
            for column in [ "Neto Ventas", "Neto Compras", 'Dif.']:
                pivoted_data_ventas_compras[column] = pivoted_data_ventas_compras[column].apply(format_currency)
            pivoted_data_ventas_compras.sort_values(by="Mes", ascending=False, inplace=True)
            st.dataframe(pivoted_data_ventas_compras, hide_index=True)

        # --- NEW FILTERS FOR RECIBIDOS/EMITIDOS ---
        # Get unique Mes and Empresa for recibidos_historicos and emitidos_historicos
        recibidos_df = recibidos_historicos[recibidos_historicos['Razon Social'] == selected_razon_social]
        emitidos_df = emitidos_historicos[emitidos_historicos['Razon Social'] == selected_razon_social]

        # MES filter (descending)
        all_meses = sorted(
            set(recibidos_df['Mes'].unique()).union(emitidos_df['Mes'].unique()),
            reverse=True
        )


        # EMPRESA filter (ascending)
        all_empresas = sorted(
            set(recibidos_df['Empresa'].unique()).union(emitidos_df['Empresa'].unique())
        )
        
        # Apply filters
        def filter_df(df):
            df = df[df['Mes'] == selected_mes]
            if selected_empresa != "(Todos)":
                df = df[df['Empresa'] == selected_empresa]
            return df
        
        sub_col1, sub_col2, sub_col3 = st.columns([2, 1, 1])
        with sub_col1:
            st.subheader("Detalle Recibidos")
        with sub_col2:
            selected_empresa = st.selectbox("Filtrar por Empresa", ["(Todos)"] + all_empresas, key="empresa_filter_tab1")
        with sub_col3:
            selected_mes = st.selectbox("Filtrar por Mes", all_meses, key="mes_filter_tab1")
        
        st.dataframe(
            filter_df(recibidos_df).drop(columns=["Razon Social", "Mes"]),
            hide_index=True
        )
        st.subheader("Detalle Emitidos")
        st.dataframe(
            filter_df(emitidos_df).drop(columns=["Razon Social", "Mes"]),
            hide_index=True
        )

    with tab2:
        tab2_col1, tab2_col2 = st.columns([2, 1])
        with tab2_col1:
            st.subheader("IVA")
            filtered_data = comprobantes_historicos[
                (comprobantes_historicos['Razon Social'] == selected_razon_social) &
                (comprobantes_historicos['Variable'].isin(['IVA Ventas', 'IVA Compras', 'Saldo IVA']))
            ]
            if not filtered_data.empty:         
                 st.bar_chart(filtered_data, x="Mes", y="Monto", color="Variable", stack=False)
            else:
                st.warning("No hay datos disponibles para la Razón Social seleccionada.")
        with tab2_col2:
            # Pivot the data to have columns Mes, IVA Ventas, IVA Compras, and Saldo IVA
            pivoted_data = filtered_data.pivot(index="Mes", columns="Variable", values="Monto").reset_index()
            pivoted_data = pivoted_data[["Mes", "IVA Ventas", "IVA Compras", "Saldo IVA"]]
            for column in [ "IVA Ventas", "IVA Compras", "Saldo IVA"]:
                pivoted_data[column] = pivoted_data[column]
            pivoted_data.sort_values(by="Mes", ascending=False, inplace=True)
            st.dataframe(pivoted_data, hide_index=True)

    with tab3:
        st.subheader("Clientes Mensual")
        filtered_data = ventas_por_empresa_cliente[
            ventas_por_empresa_cliente['Razon Social'] == selected_razon_social
        ]
        pivoted_data_clientes_tidy = filtered_data.groupby(["Empresa", "Mes"]).agg({"Neto": "sum"}).reset_index()
        pivoted_data_clientes = pivoted_data_clientes_tidy.pivot(index="Empresa", columns="Mes", values="Neto").reset_index()
        pivoted_data_clientes.fillna(0, inplace=True)  # Ensure no NaN values
        pivoted_data_clientes.iloc[:, 1:] = pivoted_data_clientes.iloc[:, 1:].round(0).astype(int)
        # Add a total column and sort by it
        pivoted_data_clientes["Total"] = pivoted_data_clientes.iloc[:, 1:].sum(axis=1)
        pivoted_data_clientes.sort_values(by="Total", ascending=False, inplace=True)
        pivoted_data_clientes_formatted = pivoted_data_clientes.copy()
        for column in pivoted_data_clientes_formatted.columns[1:]:
            pivoted_data_clientes_formatted[column] = pivoted_data_clientes_formatted[column]
        pivoted_data_clientes_formatted.rename(columns={"Empresa": "Cliente"}, inplace=True)
        st.dataframe(pivoted_data_clientes_formatted, hide_index=True)
        if not filtered_data.empty:   
                st.header("Evolución del top 10 Clientes")      
                top_10_clients = pivoted_data_clientes.head(10)
                top_10_clients_tidy = top_10_clients.melt(id_vars=["Empresa"], var_name="Mes", value_name="Neto")
                top_10_clients_tidy = top_10_clients_tidy[top_10_clients_tidy["Mes"] != "Total"]
                st.bar_chart(top_10_clients_tidy, x="Mes", y="Neto", color="Empresa", stack=False)
        else:
            st.warning("No hay datos disponibles para la Razón Social seleccionada.")
        st.subheader("Detalle Emitidos")
        st.dataframe(emitidos_historicos[emitidos_historicos['Razon Social'] == selected_razon_social].drop(columns=["Razon Social"]), 
                     hide_index=True)        
        # Pivot the data to have columns Mes and Clientes

    with tab4:
        st.subheader("Proveedores")
        filtered_data = compras_por_empresa_proveedor[
            compras_por_empresa_proveedor['Razon Social'] == selected_razon_social
        ]
        pivoted_data_proveedores_tidy = filtered_data.groupby(["Empresa", "Mes"]).agg({"Neto": "sum"}).reset_index()
        pivoted_data_proveedores = pivoted_data_proveedores_tidy.pivot(index="Empresa", columns="Mes", values="Neto").reset_index()
        pivoted_data_proveedores.fillna(0, inplace=True)
        pivoted_data_proveedores.iloc[:, 1:] = pivoted_data_proveedores.iloc[:, 1:].round(0).astype(int)
        # Add a total column and sort by i
        pivoted_data_proveedores["Total"] = pivoted_data_proveedores.iloc[:, 1:].sum(axis=1)
        pivoted_data_proveedores.sort_values(by="Total", ascending=False, inplace=True)
        pivoted_data_proveedores_formatted = pivoted_data_proveedores.copy()
        for column in pivoted_data_proveedores_formatted.columns[1:]:
            pivoted_data_proveedores_formatted[column] = pivoted_data_proveedores_formatted[column].apply(format_currency)
        pivoted_data_proveedores_formatted.rename(columns={"Empresa": "Proveedor"}, inplace=True)
        st.dataframe(pivoted_data_proveedores_formatted, hide_index=True)
        if not filtered_data.empty:   
                st.header("Evolución del top 10 Proveedores")      
                top_10_providers = pivoted_data_proveedores.head(10)
                top_10_providers_tidy = top_10_providers.melt(id_vars=["Empresa"], var_name="Mes", value_name="Neto")
                top_10_providers_tidy = top_10_providers_tidy[top_10_providers_tidy["Mes"] != "Total"]
                st.bar_chart(top_10_providers_tidy, x="Mes", y="Neto", color="Empresa", stack=False)
        else:
            st.warning("No hay datos disponibles para la Razón Social seleccionada.")
        st.subheader("Detalle Recibidos")
        st.dataframe(recibidos_historicos[recibidos_historicos['Razon Social'] == selected_razon_social].drop(columns=["Razon Social"]), 
                     hide_index=True)

    with tab5:
        st.subheader("Análisis clientes activos/perdidos")
        clientes_activos_filtered = clientes_activos[clientes_activos['Razon Social'] == selected_razon_social].drop(columns=['Razon Social'])
        st.dataframe(clientes_activos_filtered)

