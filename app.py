import streamlit as st
import pandas as pd

def fetch_data():
    emitidos = pd.read_csv('data/emitidos_unified.csv')
    emitidos['Neto'] = emitidos['Imp. Neto Gravado'] + emitidos['Imp. Neto No Gravado'] + emitidos['Imp. Op. Exentas'] 
    emitidos = emitidos[['Fecha', 'Tipo', 'Número Desde', 'Denominación Receptor', 'Neto', 'IVA', 'Imp. Total', 'razon_social']]
    emitidos['Denominación Receptor'] = emitidos['Denominación Receptor'].str.strip().str.title()

    emitidos_por_empresa = emitidos.groupby(['razon_social', 'Denominación Receptor']).agg({'Neto': 'sum', 'IVA': 'sum', 'Imp. Total': 'sum'}).reset_index()

    recibidos = pd.read_csv('data/recibidos_unified.csv')
    recibidos['Neto'] = recibidos['Imp. Neto Gravado'] + recibidos['Imp. Neto No Gravado'] + recibidos['Imp. Op. Exentas']
    recibidos = recibidos[['Fecha', 'Tipo', 'Número Desde', 'Denominación Emisor', 'Neto', 'IVA', 'Imp. Total', 'razon_social']]
    recibidos['Denominación Emisor'] = recibidos['Denominación Emisor'].str.strip().str.title()

    recibidos_por_empresa = recibidos.groupby(['razon_social', 'Denominación Emisor']).agg({'Neto': 'sum', 'IVA': 'sum', 'Imp. Total': 'sum'}).reset_index()

    resumen_contable = pd.read_csv('data/resumen_contable.csv')

    for column in resumen_contable.columns:
        if column != 'Sociedad':
            resumen_contable[column] = resumen_contable[column].apply(
                lambda x: f"${x:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".") if x >= 0 else f"(${abs(x):,.0f})".replace(",", "X").replace(".", ",").replace("X", ".")
            )
    return emitidos, recibidos, resumen_contable, emitidos_por_empresa, recibidos_por_empresa

def filter_by_razon_social(df, razon_social):
    if 'razon_social' in df.columns:
        return df[df['razon_social'] == razon_social].drop('razon_social', axis=1)
    return df

def show_page(): 
    emitidos, recibidos, resumen_contable, emitidos_por_empresa, recibidos_por_empresa = fetch_data()
       
    st.set_page_config(page_title="Resumen Contable", layout="wide")
    st.title("Resumen Contable")
    st.dataframe(resumen_contable, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.title("Comprobantes AFIP")
        st.write("Información descargada desde el sitio de 'Mis Comprobantes' de la AFIP.")
    with col2:
        razon_social_options = sorted(emitidos['razon_social'].unique().tolist())
        razon_social = st.selectbox(
            "Seleccionar Empresa", 
            options=razon_social_options,
            index=0 if razon_social_options else None)

    # Apply filter if razon_social is selected
    if razon_social:
        filtered_emitidos = filter_by_razon_social(emitidos, razon_social)
        filtered_recibidos = filter_by_razon_social(recibidos, razon_social)
        filtered_emitidos_por_empresa = filter_by_razon_social(emitidos_por_empresa, razon_social)
        filtered_recibidos_por_empresa = filter_by_razon_social(recibidos_por_empresa, razon_social)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Emitidos por Empresa")
            st.dataframe(filtered_emitidos_por_empresa, use_container_width=True, hide_index=True)
        with col2:
            st.subheader("Recibidos por Empresa")
            st.dataframe(filtered_recibidos_por_empresa, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Emitidos")
            st.dataframe(filtered_emitidos, use_container_width=True, hide_index=True)
        with col2:
            st.subheader("Recibidos")
            st.dataframe(filtered_recibidos, use_container_width=True, hide_index=True)
    else:
        st.warning("No se encontraron empresas para filtrar.")

if __name__ == "__main__":
    show_page()