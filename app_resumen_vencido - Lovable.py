import streamlit as st
import pandas as pd
from io import BytesIO
from supabase_connection import fetch_table_data

def fetch_data():
    emitidos = fetch_table_data('emitidos_mes_vencido')
    emitidos_por_empresa = emitidos.groupby(['Razon Social', 'Empresa']).agg({
        'Neto Gravado': 'sum',
        'Neto No Gravado': 'sum',
        'Op. Exentas': 'sum',
        'Neto': 'sum', 
        'IVA': 'sum', 
        'Imp. Total': 'sum'
    }).reset_index()
    emitidos_por_empresa = emitidos_por_empresa.sort_values('Neto', ascending=False)
    emitidos_por_empresa.drop(columns=['Neto'], inplace=True, errors='ignore')

    recibidos = fetch_table_data('recibidos_mes_vencido')
    recibidos_por_empresa = recibidos.groupby(['Razon Social', 'Empresa']).agg({
        'Neto Gravado': 'sum',
        'Neto No Gravado': 'sum',
        'Op. Exentas': 'sum',
        'Neto': 'sum',
        'IVA': 'sum',
        'Imp. Total': 'sum'
    }).reset_index()
    recibidos_por_empresa = recibidos_por_empresa.sort_values('Neto', ascending=False)
    recibidos_por_empresa.drop(columns=['Neto'], inplace=True, errors='ignore')

    resumen_contable = fetch_table_data('resumen_contable_mes_vencido')
    resumen_contable.drop(columns=['created_at', 'updated_at', 'fecha_generacion', 'mes', 'II BB', 'id'], inplace=True, errors='ignore')
    
    resumen_contable_total = fetch_table_data('resumen_contable_total')
    resumen_contable_total.drop(columns=['created_at', 'updated_at', 'fecha_generacion', 'mes', 'II BB', 'id'], inplace=True, errors='ignore')
    
    return (
        emitidos, recibidos, resumen_contable, resumen_contable_total, emitidos_por_empresa, recibidos_por_empresa
    )

def filter_by_razon_social(df, razon_social):
    if 'Razon Social' in df.columns:
        return df[df['Razon Social'] == razon_social].drop('Razon Social', axis=1)
    if 'Sociedad' in df.columns:
        return df[df['Sociedad'] == razon_social].drop('Sociedad', axis=1)
    return df

def show_page(username):
    with open('data/leyenda_resumen_contable_mes_vencido.txt', encoding='utf-8') as f:
        leyenda = f.read()
    coltitle, collogo= st.columns([7, 1])
    with coltitle:
        st.title(leyenda)
    with collogo:   
        st.image("data/logo.png", width=160)
    #st.info("En construcción")
    # Get data
    (
        emitidos, recibidos, resumen_contable, resumen_contable_total, emitidos_por_empresa, recibidos_por_empresa
    ) = fetch_data()
    

    col_title, col_download = st.columns([3, 1])
    
    with st.container():
        st.dataframe(resumen_contable_total, use_container_width=True, hide_index=True)
    
    st.header("Detalle por Sociedad")
    with st.container():
        st.dataframe(resumen_contable, use_container_width=True, hide_index=True, height=460)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.header("Comprobantes AFIP")
        st.write("Información descargada desde el sitio de 'Mis Comprobantes' de la AFIP.")
    with col2:
        razon_social_options = sorted(emitidos['Razon Social'].unique().tolist())
        razon_social = st.selectbox(
            "Seleccionar Empresa", 
            options=razon_social_options,
            index=0 if razon_social_options else None,
            key="display_selector")
        
        # Now that razon_social is defined, we can add the download button
        with col_download:
            filtered_emitidos = filter_by_razon_social(emitidos, razon_social)
            filtered_recibidos = filter_by_razon_social(recibidos, razon_social)
            filtered_emitidos_por_empresa = filter_by_razon_social(emitidos_por_empresa, razon_social)
            filtered_recibidos_por_empresa = filter_by_razon_social(recibidos_por_empresa, razon_social)
            
            # Download functionality removed - to_excel_multiple_sheets function not available
       
    # Apply filter if razon_social is selected

    if razon_social:
        filtered_emitidos = filter_by_razon_social(emitidos, razon_social)
        filtered_recibidos = filter_by_razon_social(recibidos, razon_social)
        filtered_emitidos_por_empresa = filter_by_razon_social(emitidos_por_empresa, razon_social)
        filtered_recibidos_por_empresa = filter_by_razon_social(recibidos_por_empresa, razon_social)
        
    # Show tables with standard styling
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ventas")
        st.write("Total mensual Emitidos por Cliente")
        # Show metrics for filtered_emitidos_por_empresa
        total_gravado = filtered_emitidos_por_empresa['Neto Gravado'].sum()
        total_no_gravado = filtered_emitidos_por_empresa['Neto No Gravado'].sum()
        total_exentas = filtered_emitidos_por_empresa['Op. Exentas'].sum()
        total_iva = filtered_emitidos_por_empresa['IVA'].sum()
        total_imp_total = filtered_emitidos_por_empresa['Imp. Total'].sum()

        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        # Use markdown for smaller font size in metrics
        col_m1.markdown(f"<span style='font-size:14px'><b>Neto Gravado</b><br>${total_gravado:,.0f}</span>", unsafe_allow_html=True)
        col_m2.markdown(f"<span style='font-size:14px'><b>Neto No Gravado</b><br>${total_no_gravado:,.0f}</span>", unsafe_allow_html=True)
        col_m3.markdown(f"<span style='font-size:14px'><b>Op. Exentas</b><br>${total_exentas:,.0f}</span>", unsafe_allow_html=True)
        col_m4.markdown(f"<span style='font-size:14px'><b>IVA</b><br>${total_iva:,.0f}</span>", unsafe_allow_html=True)
        col_m5.markdown(f"<span style='font-size:14px'><b>Imp. Total</b><br>${total_imp_total:,.0f}</span>", unsafe_allow_html=True)
        with st.container():
            st.dataframe(filtered_emitidos_por_empresa, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("Compras")
        st.write("Total mensual Recibidos por Proveedor")
        # Show metrics for filtered_recibidos_por_empresa
        total_gravado = filtered_recibidos_por_empresa['Neto Gravado'].sum()
        total_no_gravado = filtered_recibidos_por_empresa['Neto No Gravado'].sum()
        total_exentas = filtered_recibidos_por_empresa['Op. Exentas'].sum()
        total_iva = filtered_recibidos_por_empresa['IVA'].sum()
        total_imp_total = filtered_recibidos_por_empresa['Imp. Total'].sum()

        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        col_m1.markdown(f"<span style='font-size:14px'><b>Neto Gravado</b><br>${total_gravado:,.0f}</span>", unsafe_allow_html=True)
        col_m2.markdown(f"<span style='font-size:14px'><b>Neto No Gravado</b><br>${total_no_gravado:,.0f}</span>", unsafe_allow_html=True)
        col_m3.markdown(f"<span style='font-size:14px'><b>Op. Exentas</b><br>${total_exentas:,.0f}</span>", unsafe_allow_html=True)
        col_m4.markdown(f"<span style='font-size:14px'><b>IVA</b><br>${total_iva:,.0f}</span>", unsafe_allow_html=True)
        col_m5.markdown(f"<span style='font-size:14px'><b>Imp. Total</b><br>${total_imp_total:,.0f}</span>", unsafe_allow_html=True)
        with st.container():
            st.dataframe(filtered_recibidos_por_empresa, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Detalle Comprobantes Emitidos")
        with st.container():
            st.dataframe(filtered_emitidos, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("Detalle Comprobantes Recibidos")
        with st.container():
            st.dataframe(filtered_recibidos, use_container_width=True, hide_index=True)
