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
    return df

def to_excel(df):
    """Convert a DataFrame to Excel bytes."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    processed_data = output.getvalue()
    return processed_data

def fetch_data(): 
    emitidos = pd.read_csv('C:\\Users\\facun\\OneDrive\\Documentos\\GitHub\\comprobantes_afip_actual\\emitidos.csv')
    recibidos =  pd.read_csv('C:\\Users\\facun\\OneDrive\\Documentos\\GitHub\\comprobantes_afip_actual\\recibidos.csv')
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


    return resumen_contable_mes_actual, resumen_contable_mes_actual_excel, leyenda, recibidos_por_empresa, recibidos_por_empresa_excel, emitidos_por_empresa, emitidos_por_empresa_excel

def show_page(username):
    resumen_contable_mes_actual, resumen_contable_mes_actual_excel, leyenda, recibidos_por_empresa, recibidos_por_empresa_excel, emitidos_por_empresa, emitidos_por_empresa_excel = fetch_data()
    
    # Apply user-based filtering
    resumen_contable_mes_actual = filter_restricted_data(resumen_contable_mes_actual, username)
    resumen_contable_mes_actual_excel = filter_restricted_data(resumen_contable_mes_actual_excel, username)
    
    st.title(leyenda)
    st.dataframe(resumen_contable_mes_actual, use_container_width=True, hide_index=True)
    
    st.download_button(
        label="Descargar Resumen Contable (Excel)",
        data=to_excel(resumen_contable_mes_actual_excel),
        file_name='Resumen_Contable_Mes_Actual.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    with col1:
        st.header("Detalle por Emisor/Receptor")
    with col2:
        razon_social_options = sorted(emitidos['razon_social'].unique().tolist())
        razon_social = st.selectbox(
            "Seleccionar Empresa", 
            options=razon_social_options,
            index=0 if razon_social_options else None,
            key="display_selector"
        )
        
        # Now that razon_social is defined, we can add the download button
        with col_download:
            st.image("data/logo.png")
            filtered_emitidos_excel = filter_by_razon_social(emitidos_excel, razon_social)
            filtered_recibidos_excel = filter_by_razon_social(recibidos_excel, razon_social)
            filtered_emitidos_por_empresa_excel = filter_by_razon_social(emitidos_por_empresa_excel, razon_social)
            filtered_recibidos_por_empresa_excel = filter_by_razon_social(recibidos_por_empresa_excel, razon_social)
            
            st.download_button(
                label="Descargar informe en Excel",
                data=to_excel_multiple_sheets(
                    resumen_contable_excel,
                    filtered_emitidos_excel,
                    filtered_recibidos_excel,
                    filtered_emitidos_por_empresa_excel,
                    filtered_recibidos_por_empresa_excel
                ),
                file_name=f"resumen_contable_{razon_social}.xlsx" if razon_social else "resumen_contable_completo.xlsx")
       
    # Apply filter if razon_social is selected
    filtered_emitidos = filter_by_razon_social(emitidos, razon_social)
    filtered_recibidos = filter_by_razon_social(recibidos, razon_social)
    filtered_emitidos_por_empresa = filter_by_razon_social(emitidos_por_empresa, razon_social)
    filtered_recibidos_por_empresa = filter_by_razon_social(recibidos_por_empresa, razon_social)
    
    # Show tables with standard styling
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Emitidos por Empresa")
        with st.container():
            st.dataframe(filtered_emitidos_por_empresa, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("Recibidos por Empresa")
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

