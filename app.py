import streamlit as st
import pandas as pd

def fetch_data():
    emitidos = pd.read_csv('data/emitidos_unified.csv')
    recibidos = pd.read_csv('data/recibidos_unified.csv')
    return emitidos, recibidos

def show_page(): 
    emitidos, recibidos = fetch_data()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Emitidos")
        st.dataframe(emitidos, use_container_width=True)
    with col2:
        st.subheader("Recibidos")
        st.dataframe(recibidos, use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(page_title="Emitidos vs Recibidos", layout="wide")
    st.title("Emitidos vs Recibidos")
    st.write("Comparativa de datos emitidos y recibidos")
    show_page()