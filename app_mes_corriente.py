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

def filter_by_razon_social(df, razon_social):
    if 'razon_social' in df.columns:
        return df[df['razon_social'] == razon_social].drop('razon_social', axis=1)
    if 'Sociedad' in df.columns:
        return df[df['Sociedad'] == razon_social].drop('Sociedad', axis=1)
    return df


def to_excel_multiple_sheets(resumen_contable_mes_actual_excel, emitidos_excel, recibidos_excel, emitidos_por_empresa_excel, recibidos_por_empresa_excel):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet
    resumen_contable_mes_actual_excel.to_excel(writer, sheet_name='Resumen Contable', index=False)
    emitidos_por_empresa_excel.to_excel(writer, sheet_name='Emitidos por Empresa', index=False)
    recibidos_por_empresa_excel.to_excel(writer, sheet_name='Recibidos por Empresa', index=False)
    emitidos_excel.to_excel(writer, sheet_name='Detalle Emitidos', index=False)
    recibidos_excel.to_excel(writer, sheet_name='Detalle Recibidos', index=False)
    
    # Close the Pandas Excel writer and output the Excel file
    writer.close()
    processed_data = output.getvalue()
    return processed_data


def fetch_data(): 
    emitidos = pd.read_csv('data/emitidos_historico.csv')
    emitidos = emitidos[emitidos['Fecha'].str.endswith('/05/2025')]
    emitidos_excel = emitidos.copy()

    recibidos = pd.read_csv('data/recibidos_historico.csv')
    recibidos = recibidos[recibidos['Fecha'].str.endswith('/05/2025')]
    recibidos_excel = recibidos.copy()

    resumen_contable_mes_actual = pd.read_csv('data/resumen_contable_mes_actual.csv')
    resumen_contable_mes_actual_excel = resumen_contable_mes_actual.copy()
    for column in resumen_contable_mes_actual.columns:
        if column != 'Sociedad':
            resumen_contable_mes_actual[column] = resumen_contable_mes_actual[column].apply(format_currency)
    with open('data/leyenda_resumen_contable_mes_actual.txt', 'r', encoding='utf-8') as file:
        leyenda = file.read()
    #Recibidos por empresa
    recibidos_por_empresa = pd.read_csv('data/recibidos_por_empresa_mes_actual.csv')
    recibidos_por_empresa_excel = recibidos_por_empresa.copy()
    for column in ['Neto', 'IVA', 'Imp. Total']:
        recibidos_por_empresa[column] = recibidos_por_empresa[column].apply(format_currency)
    #Emitidos por empresa
    emitidos_por_empresa = pd.read_csv('data/emitidos_por_empresa_mes_actual.csv')
    emitidos_por_empresa_excel = emitidos_por_empresa.copy()
    for column in ['Neto', 'IVA', 'Imp. Total']:
        emitidos_por_empresa[column] = emitidos_por_empresa[column].apply(format_currency)


    return emitidos, recibidos, emitidos_excel, recibidos_excel, resumen_contable_mes_actual, resumen_contable_mes_actual_excel, leyenda, recibidos_por_empresa, recibidos_por_empresa_excel, emitidos_por_empresa, emitidos_por_empresa_excel

def show_page(username):
    emitidos, recibidos, emitidos_excel, recibidos_excel, resumen_contable_mes_actual, resumen_contable_mes_actual_excel, leyenda, recibidos_por_empresa, recibidos_por_empresa_excel, emitidos_por_empresa, emitidos_por_empresa_excel = fetch_data()
    
    # Apply user-based filtering
    resumen_contable_mes_actual = filter_restricted_data(resumen_contable_mes_actual, username)
    resumen_contable_mes_actual_excel = filter_restricted_data(resumen_contable_mes_actual_excel, username)
    st.title(leyenda)
    col_title, col_download = st.columns([3, 1])
    with col_download:
        st.image("data/logo.png")
        st.download_button(
            label="Descargar informe en Excel",
            data=to_excel_multiple_sheets(resumen_contable_mes_actual_excel, emitidos_excel, recibidos_excel, emitidos_por_empresa_excel, recibidos_por_empresa_excel),
            file_name='Resumen_Contable_Mes_Actual.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    st.dataframe(resumen_contable_mes_actual, use_container_width=True, hide_index=True)
    
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.header("Detalle por Emisor/Receptor")
        st.write("Información descargada desde el sitio de 'Mis Comprobantes' de la AFIP hasta la fecha indicada")
    with col2:
        razon_social_options = sorted(emitidos['razon_social'].unique().tolist())
        razon_social = st.selectbox(
            "Seleccionar Empresa", 
            options=razon_social_options,
            index=0 if razon_social_options else None,
            key="display_selector"
        )

    if razon_social:
        filtered_emitidos = filter_by_razon_social(emitidos, razon_social)
        filtered_recibidos = filter_by_razon_social(recibidos, razon_social)
        filtered_emitidos_por_empresa = filter_by_razon_social(emitidos_por_empresa, razon_social)
        filtered_recibidos_por_empresa = filter_by_razon_social(recibidos_por_empresa, razon_social)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Emitidos por Empresa")
        with st.container():
            st.dataframe(filtered_emitidos_por_empresa, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("Recibidos por Empresa")
        with st.container():
            st.dataframe(filtered_recibidos_por_empresa, use_container_width=True, hide_index=True)
    
    # Create new columns for second pair of tables
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Detalle Comprobantes Emitidos")
        with st.container():
            st.dataframe(filtered_emitidos, use_container_width=True, hide_index=True)
    with col4:
        st.subheader("Detalle Comprobantes Recibidos")
        with st.container():
            st.dataframe(filtered_recibidos, use_container_width=True, hide_index=True)