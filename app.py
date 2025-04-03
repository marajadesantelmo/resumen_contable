import streamlit as st
import pandas as pd

def fetch_data():
    emitidos = pd.read_csv('data/emitidos_unified.csv')
    recibidos = pd.read_csv('data/recibidos_unified.csv')
    return emitidos, recibidos

def filter_by_razon_social(df, razon_social):
    if 'razon_social' in df.columns:
        return df[df['razon_social'] == razon_social].drop('razon_social', axis=1)
    return df

def show_page(): 
    emitidos, recibidos = fetch_data()
    
    # Get unique razon_social values from emitidos (assuming this is where the field exists)
    razon_social_options = []
    if 'razon_social' in emitidos.columns:
        razon_social_options = sorted(emitidos['razon_social'].unique().tolist())

    # Filter selector
    razon_social = st.sidebar.selectbox(
        "Seleccionar Empresa", 
        options=razon_social_options,
        index=0 if razon_social_options else None
    )

    # Apply filter if razon_social is selected
    if razon_social:
        filtered_emitidos = filter_by_razon_social(emitidos, razon_social)
        filtered_recibidos = filter_by_razon_social(recibidos, razon_social)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Emitidos")
            st.dataframe(filtered_emitidos, use_container_width=True)
        with col2:
            st.subheader("Recibidos")
            st.dataframe(filtered_recibidos, use_container_width=True)
    else:
        st.warning("No se encontraron empresas para filtrar.")

if __name__ == "__main__":
    st.set_page_config(page_title="Comprobantes AFIP", layout="wide")
    st.title("Comprobantes AFIP")
    st.write("Información descargada desde el sitio de 'Mis Comprobantes' de la AFIP.")
    show_page()