import streamlit as st
st.set_page_config(page_title="Resumen Contable", layout="wide")
import pandas as pd
from streamlit_cookies_manager import EncryptedCookieManager
import io
from io import BytesIO

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

# Login function
USERNAMES = ["Manuel", "FU"]
PASSWORDS = ["1234", "urtubey"]

def login(username, password):
    if username in USERNAMES and password == PASSWORDS[USERNAMES.index(username)]:
        return True
    return False

def to_excel_multiple_sheets(resumen_contable, emitidos, recibidos, emitidos_por_empresa, recibidos_por_empresa):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # Convert resumen_contable to numerical values for Excel
    rc_excel = resumen_contable.copy()
    for col in rc_excel.columns:
        if col != 'Sociedad':
            # This removes currency formatting and converts to float
            rc_excel[col] = rc_excel[col].str.replace('$', '').str.replace('.', '').str.replace(',', '.').str.replace('(', '-').str.replace(')', '')
            rc_excel[col] = pd.to_numeric(rc_excel[col], errors='coerce')
    
    # Write each dataframe to a different worksheet
    rc_excel.to_excel(writer, sheet_name='Resumen Contable', index=False)
    emitidos_por_empresa.to_excel(writer, sheet_name='Emitidos por Empresa', index=False)
    recibidos_por_empresa.to_excel(writer, sheet_name='Recibidos por Empresa', index=False)
    emitidos.to_excel(writer, sheet_name='Detalle Emitidos', index=False)
    recibidos.to_excel(writer, sheet_name='Detalle Recibidos', index=False)
    
    # Close the Pandas Excel writer and output the Excel file
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def show_page(): 
    emitidos, recibidos, resumen_contable, emitidos_por_empresa, recibidos_por_empresa = fetch_data()
    
    
    # Initialize cookies manager
    cookies = EncryptedCookieManager(prefix="resumen_contable_", password="secure_password_here")
    
    if not cookies.ready():
        st.stop()
    
    # Check if user is already logged in
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = cookies.get("logged_in") == "True"
    if 'username' not in st.session_state:
        st.session_state.username = cookies.get("username", "")
    
    if not st.session_state.logged_in:
        st.title("Resumen Contable - Login")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                cookies["logged_in"] = "True"
                cookies["username"] = username
                cookies.save()
                st.success("¡Bienvenido/a!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    else:
        # Main application
        # Create a row with title and download button
        col_title, col_download = st.columns([3, 1])
        with col_title:
            st.title("Resumen Contable")
        with col_download:
            st.write("")  # Add some space
            st.write("")  # Add some space to align with title
            razon_social_options = sorted(emitidos['razon_social'].unique().tolist())
            razon_social = st.selectbox(
                "Seleccionar Empresa", 
                options=razon_social_options,
                index=0 if razon_social_options else None)
            
            filtered_emitidos = filter_by_razon_social(emitidos, razon_social)
            filtered_recibidos = filter_by_razon_social(recibidos, razon_social)
            filtered_emitidos_por_empresa = filter_by_razon_social(emitidos_por_empresa, razon_social)
            filtered_recibidos_por_empresa = filter_by_razon_social(recibidos_por_empresa, razon_social)
            
            st.download_button(
                label="Descargar informe en Excel",
                data=to_excel_multiple_sheets(
                    resumen_contable,
                    filtered_emitidos,
                    filtered_recibidos,
                    filtered_emitidos_por_empresa,
                    filtered_recibidos_por_empresa
                ),
                file_name=f"resumen_contable_{razon_social}.xlsx" if razon_social else "resumen_contable_completo.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        # Display the main content
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
            st.subheader("Detalle Comprobantes Emitidos")
            st.dataframe(filtered_emitidos, use_container_width=True, hide_index=True)
        with col2:
            st.subheader("Detalle Comprobantes Recibidos")
            st.dataframe(filtered_recibidos, use_container_width=True, hide_index=True)
        
        # Add logout button at the end of the body
        if st.button("Cerrar sesión"):
            cookies["logged_in"] = "False"
            cookies.pop("username", None)
            cookies.save()
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

if __name__ == "__main__":
    show_page()