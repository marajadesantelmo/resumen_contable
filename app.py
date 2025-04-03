import streamlit as st
st.set_page_config(page_title="Resumen Contable", layout="wide")
import pandas as pd
from streamlit_cookies_manager import EncryptedCookieManager
import io
from io import BytesIO

# Add custom CSS for solarized theme and fancy table formatting
def apply_custom_css():
    st.markdown("""
    <style>
    /* Solarized theme variables */
    :root {
        --base03: #002b36;
        --base02: #073642;
        --base01: #586e75;
        --base00: #657b83;
        --base0: #839496;
        --base1: #93a1a1;
        --base2: #eee8d5;
        --base3: #fdf6e3;
        --yellow: #b58900;
        --orange: #cb4b16;
        --red: #dc322f;
        --magenta: #d33682;
        --violet: #6c71c4;
        --blue: #268bd2;
        --cyan: #2aa198;
        --green: #859900;
    }

    /* Force dark mode for the entire app, regardless of system settings */
    .stApp {
        background-color: var(--base03) !important;
        color: var(--base0) !important;
    }

    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        color: var(--base1) !important;
        font-weight: bold;
    }
    
    /* Force dark mode on all text elements */
    p, span, div {
        color: var(--base0) !important;
    }
    
    /* Fancy table styling - dark mode always */
    div[data-testid="stDataFrame"] table {
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    div[data-testid="stDataFrame"] thead tr th {
        background-color: var(--base02) !important;
        color: var(--base2) !important;
        padding: 12px 15px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.9em !important;
        border: none !important;
        position: sticky;
        top: 0;
        z-index: 100;
    }

    /* Dark table rows */
    div[data-testid="stDataFrame"] tbody tr:nth-child(even) {
        background-color: var(--base02) !important;
    }
    
    div[data-testid="stDataFrame"] tbody tr:nth-child(odd) {
        background-color: var(--base03) !important;
    }
    
    div[data-testid="stDataFrame"] tbody tr:hover {
        background-color: #0a4252 !important;
    }

    div[data-testid="stDataFrame"] tbody td {
        padding: 10px 15px !important;
        border: none !important;
        border-bottom: 1px solid #15414b !important;
        color: var(--base1) !important;
    }

    /* Style currency values */
    div[data-testid="stDataFrame"] td:has(div[style*="text-align: right"]) {
        font-family: 'Courier New', monospace;
        font-weight: 500;
        color: var(--cyan) !important;
    }

    /* Buttons styling */
    .stButton button {
        background-color: var(--blue);
        color: white !important;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        background-color: var(--cyan);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
    }

    /* Select box styling */
    div[data-baseweb="select"] {
        border-radius: 6px;
        border: 1px solid var(--base01);
        background-color: var(--base02) !important;
    }
    
    /* Input fields */
    .stTextInput input, .stTextInput textarea, .stNumberInput input {
        background-color: var(--base02) !important;
        color: var(--base1) !important;
        border: 1px solid var(--base01) !important;
    }
    
    /* Login container */
    .login-container {
        background-color: var(--base02) !important;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Streamlit widgets */
    .stSelectbox, .stMultiselect {
        background-color: var(--base02) !important;
        color: var(--base1) !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--base03) !important;
        border-right: 1px solid var(--base02);
    }
    
    /* Success/info messages */
    div[data-baseweb="notification"] {
        background-color: var(--base02) !important;
    }
    
    /* Links */
    a {
        color: var(--blue) !important;
    }
    a:hover {
        color: var(--cyan) !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

# Login function
USERNAMES = ["Manuel", "FU"]
PASSWORDS = ["1234", "urtubey"]

def login(username, password):
    if username in USERNAMES and password == PASSWORDS[USERNAMES.index(username)]:
        return True
    return False

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

def show_page(): 
    # Apply our custom CSS at the beginning
    apply_custom_css()
    
    # Get both formatted data (for display) and raw data (for Excel)
    (
        emitidos, recibidos, resumen_contable, resumen_contable_total, emitidos_por_empresa, recibidos_por_empresa,
        emitidos_excel, recibidos_excel, resumen_contable_excel, emitidos_por_empresa_excel, recibidos_por_empresa_excel
    ) = fetch_data()
    
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
        st.markdown('<h1 style="text-align: center; margin-bottom: 30px; color: #93a1a1;">Resumen Contable - Login</h1>', unsafe_allow_html=True)
        
        # Add a container with some styling for the login form
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown('<div class="login-container" style="padding: 20px; background-color: #073642; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);">', unsafe_allow_html=True)
                username = st.text_input("Usuario")
                password = st.text_input("Contraseña", type="password")
                
                if st.button("Ingresar", key="login_button"):
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
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Apply user-based filtering
        username = st.session_state.username
        
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
        
        # Main application
        # Create a row with title and improve styling
        st.markdown('<div style="padding: 10px 0; border-bottom: 2px solid #586e75; margin-bottom: 20px;">', unsafe_allow_html=True)
        col_title, col_download = st.columns([3, 1])
        with col_title:
            st.markdown('<h1 style="margin-bottom: 0; color: #93a1a1;">Resumen Contable - Marzo 2025</h1>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
            
        # Display total summary with improved table styles
        st.dataframe(resumen_contable_total, use_container_width=True, hide_index=True)
        
        st.markdown('<h2>Detalle por Sociedad</h2>', unsafe_allow_html=True)
        st.dataframe(resumen_contable, use_container_width=True, hide_index=True)

        # Improved section divider
        st.markdown('<div style="margin: 30px 0; border-top: 1px solid #586e75;"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<h2>Comprobantes AFIP</h2>', unsafe_allow_html=True)
            st.write("Información descargada desde el sitio de 'Mis Comprobantes' de la AFIP.")
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
                st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
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
                st.markdown('</div>', unsafe_allow_html=True)
           
        # Apply filter if razon_social is selected
        filtered_emitidos = filter_by_razon_social(emitidos, razon_social)
        filtered_recibidos = filter_by_razon_social(recibidos, razon_social)
        filtered_emitidos_por_empresa = filter_by_razon_social(emitidos_por_empresa, razon_social)
        filtered_recibidos_por_empresa = filter_by_razon_social(recibidos_por_empresa, razon_social)
        
        # Show tables with improved styling
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<h3 style="color: #268bd2;">Emitidos por Empresa</h3>', unsafe_allow_html=True)
            st.dataframe(filtered_emitidos_por_empresa, use_container_width=True, hide_index=True)
        with col2:
            st.markdown('<h3 style="color: #2aa198;">Recibidos por Empresa</h3>', unsafe_allow_html=True)
            st.dataframe(filtered_recibidos_por_empresa, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<h3 style="color: #268bd2;">Detalle Comprobantes Emitidos</h3>', unsafe_allow_html=True)
            st.dataframe(filtered_emitidos, use_container_width=True, hide_index=True)
        with col2:
            st.markdown('<h3 style="color: #2aa198;">Detalle Comprobantes Recibidos</h3>', unsafe_allow_html=True)
            st.dataframe(filtered_recibidos, use_container_width=True, hide_index=True)
        
        # Add logout button with improved styling
        st.markdown('<div style="display: flex; justify-content: center; margin-top: 30px;">', unsafe_allow_html=True)
        if st.button("Cerrar sesión"):
            cookies["logged_in"] = "False"
            cookies.pop("username", None)
            cookies.save()
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    show_page()