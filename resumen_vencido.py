import streamlit as st
import pandas as pd
from io import BytesIO

def format_currency(x):
    """Format number as Argentine peso currency"""
    return f"${x:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".") if x >= 0 else f"(${abs(x):,.0f})".replace(",", "X").replace(".", ",").replace("X", ".")

def fetch_data():
    # Load emitidos data
    emitidos = pd.read_csv('data/emitidos_unified.csv')
    emitidos['Neto'] = emitidos['Imp. Neto Gravado'] + emitidos['Imp. Neto No Gravado'] + emitidos['Imp. Op. Exentas'] 
    emitidos = emitidos[['Fecha', 'Tipo', 'Número Desde', 'Denominación Receptor', 'Neto', 'IVA', 'Imp. Total', 'razon_social']]
    emitidos['Denominación Receptor'] = emitidos['Denominación Receptor'].str.strip().str.title()
    
    # Clean the 'Sociedad' column by removing specified substrings
    sociedad_replacements = ["S.A.", "Srl", "Sociedad Anonima", "Company S A C", "S. R. L."]
    for replacement in sociedad_replacements:
        emitidos['razon_social'] = emitidos['razon_social'].str.replace(replacement, '', regex=False).str.strip()

    # Store raw values for Excel export but don't show in UI
    emitidos_excel = emitidos.copy()
    
    # Format currency columns in emitidos for display
    for column in ['Neto', 'IVA', 'Imp. Total']:
        emitidos[column] = emitidos[column].apply(format_currency)

    # Create summary by company
    emitidos_por_empresa = emitidos_excel.groupby(['razon_social', 'Denominación Receptor']).agg({
        'Neto': 'sum', 
        'IVA': 'sum', 
        'Imp. Total': 'sum'
    }).reset_index()
    
    # Sort by Imp. Total in descending order
    emitidos_por_empresa = emitidos_por_empresa.sort_values('Imp. Total', ascending=False)
    
    # Create a copy for Excel export
    emitidos_por_empresa_excel = emitidos_por_empresa.copy()
    
    # Format currency columns for display
    for column in ['Neto', 'IVA', 'Imp. Total']:
        emitidos_por_empresa[column] = emitidos_por_empresa[column].apply(format_currency)

    # Load recibidos data
    recibidos = pd.read_csv('data/recibidos_unified.csv')
    recibidos['Neto'] = recibidos['Imp. Neto Gravado'] + recibidos['Imp. Neto No Gravado'] + recibidos['Imp. Op. Exentas']
    recibidos = recibidos[['Fecha', 'Tipo', 'Número Desde', 'Denominación Emisor', 'Neto', 'IVA', 'Imp. Total', 'razon_social']]
    recibidos['Denominación Emisor'] = recibidos['Denominación Emisor'].str.strip().str.title()
    
    # Clean the 'razon_social' column by removing specified substrings
    sociedad_replacements = ["S.A.", "Srl", "Sociedad Anonima", "Company S A C", "S. R. L."]
    for replacement in sociedad_replacements:
        recibidos['razon_social'] = recibidos['razon_social'].str.replace(replacement, '', regex=False).str.strip()

    # Store raw values for Excel export but don't show in UI
    recibidos_excel = recibidos.copy()
    
    # Format currency columns in recibidos for display
    for column in ['Neto', 'IVA', 'Imp. Total']:
        recibidos[column] = recibidos[column].apply(format_currency)

    # Create summary by company
    recibidos_por_empresa = recibidos_excel.groupby(['razon_social', 'Denominación Emisor']).agg({
        'Neto': 'sum', 
        'IVA': 'sum', 
        'Imp. Total': 'sum'
    }).reset_index()
    
    # Sort by Imp. Total in descending order
    recibidos_por_empresa = recibidos_por_empresa.sort_values('Imp. Total', ascending=False)
    
    # Create a copy for Excel export
    recibidos_por_empresa_excel = recibidos_por_empresa.copy()
    
    # Format currency columns for display
    for column in ['Neto', 'IVA', 'Imp. Total']:
        recibidos_por_empresa[column] = recibidos_por_empresa[column].apply(format_currency)

    # Load resumen contable data
    resumen_contable = pd.read_csv('data/resumen_contable.csv')
    
    # Create a copy for Excel export
    resumen_contable_excel = resumen_contable.copy()

    # Format currency columns for display
    for column in resumen_contable.columns:
        if column != 'Sociedad':
            resumen_contable[column] = resumen_contable[column].apply(format_currency)

    resumen_contable_total = pd.read_csv('data/resumen_contable_total.csv')

    for column in resumen_contable_total.columns:
        if column != 'Sociedad':
            resumen_contable_total[column] = resumen_contable_total[column].apply(format_currency)
            
    return (
        emitidos, recibidos, resumen_contable, resumen_contable_total, emitidos_por_empresa, recibidos_por_empresa,
        emitidos_excel, recibidos_excel, resumen_contable_excel, emitidos_por_empresa_excel, recibidos_por_empresa_excel
    )

def filter_by_razon_social(df, razon_social):
    if 'razon_social' in df.columns:
        return df[df['razon_social'] == razon_social].drop('razon_social', axis=1)
    return df

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

def to_excel_multiple_sheets(resumen_contable_excel, emitidos_excel, recibidos_excel, emitidos_por_empresa_excel, recibidos_por_empresa_excel):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet
    resumen_contable_excel.to_excel(writer, sheet_name='Resumen Contable', index=False)
    emitidos_por_empresa_excel.to_excel(writer, sheet_name='Emitidos por Empresa', index=False)
    recibidos_por_empresa_excel.to_excel(writer, sheet_name='Recibidos por Empresa', index=False)
    emitidos_excel.to_excel(writer, sheet_name='Detalle Emitidos', index=False)
    recibidos_excel.to_excel(writer, sheet_name='Detalle Recibidos', index=False)
    
    # Close the Pandas Excel writer and output the Excel file
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def show_page(username):
    st.title("Resumen Contable - Mes Vencido (Marzo 2025)")
    
    # Get both formatted data (for display) and raw data (for Excel)
    (
        emitidos, recibidos, resumen_contable, resumen_contable_total, emitidos_por_empresa, recibidos_por_empresa,
        emitidos_excel, recibidos_excel, resumen_contable_excel, emitidos_por_empresa_excel, recibidos_por_empresa_excel
    ) = fetch_data()
    
    # Filter data based on user permissions
    emitidos = filter_restricted_data(emitidos, username)
    recibidos = filter_restricted_data(recibidos, username)
    emitidos_por_empresa = filter_restricted_data(emitidos_por_empresa, username)
    recibidos_por_empresa = filter_restricted_data(recibidos_por_empresa, username)
    resumen_contable = filter_restricted_data(resumen_contable, username)
    
    # Also filter the Excel data
    emitidos_excel = filter_restricted_data(emitidos_excel, username)
    recibidos_excel = filter_restricted_data(recibidos_excel, username)
    emitidos_por_empresa_excel = filter_restricted_data(emitidos_por_empresa_excel, username)
    recibidos_por_empresa_excel = filter_restricted_data(recibidos_por_empresa_excel, username)
    resumen_contable_excel = filter_restricted_data(resumen_contable_excel, username)
    

    col_title, col_download = st.columns([3, 1])
    
    with st.container():
        st.dataframe(resumen_contable_total, use_container_width=True, hide_index=True)
    
    st.header("Detalle por Sociedad")
    with st.container():
        st.dataframe(resumen_contable, use_container_width=True, hide_index=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.header("Comprobantes AFIP")
        st.write("Información descargada desde el sitio de 'Mis Comprobantes' de la AFIP.")
    with col2:
        razon_social_options = sorted(emitidos['razon_social'].unique().tolist())
        razon_social = st.selectbox(
            "Seleccionar Empresa", 
            options=razon_social_options,
            index=0 if razon_social_options else None,
            key="display_selector")
        
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

    if razon_social:
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
