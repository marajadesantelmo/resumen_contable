"""
Procesamiento de csv ya descomprimidos
"""

import os
import pandas as pd
import re
import time
import shutil
import zipfile

from tokens import url_supabase, key_supabase
from supabase import create_client, Client
from datetime import datetime

supabase_client = create_client(url_supabase, key_supabase)

def clean_dataframe_for_db(df):
    """Clean DataFrame for database insertion"""
    df_clean = df.copy()
    
    # Replace NaN values with None for proper NULL handling
    df_clean = df_clean.where(pd.notnull(df_clean), None)
    
    # Keep original column names as they match the database schema exactly
    # No need to convert column names since we're using quoted identifiers in SQL
    
    return df_clean

def convert_date_format(date_str):
    """Convert date from DD/MM/YYYY to YYYY-MM-DD format"""
    try:
        if pd.isna(date_str) or date_str is None:
            return None
        return datetime.strptime(str(date_str), '%d/%m/%Y').strftime('%Y-%m-%d')
    except:
        return None

def upload_dataframe_to_supabase(df, table_name, batch_size=100):
    """Upload DataFrame to Supabase table in batches with upsert functionality"""
    try:
        print(f"Uploading {len(df)} records to {table_name}...")
        
        # Clean the DataFrame
        df_clean = clean_dataframe_for_db(df)
        
        # Convert dates for historical tables
        if 'Fecha' in df_clean.columns:
            df_clean['Fecha'] = df_clean['Fecha'].apply(convert_date_format)
        
        # Convert DataFrame to list of dictionaries
        records = df_clean.to_dict('records')
        
        # Upload in batches
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            try:
                # Use upsert for tables with unique constraints
                if table_name in ['comprobantes_historicos', 'ventas_historico_mensual', 
                                'compras_historico_mensual', 'ventas_historico_cliente', 
                                'compras_historico_proveedor', 'resumen_contable_mes_vencido',
                                'resumen_contable_total', 'clientes_activos']:
                    result = supabase_client.table(table_name).upsert(batch).execute()
                else:
                    # Clear existing data and insert new for other tables
                    if i == 0:  # Only clear on first batch
                        supabase_client.table(table_name).delete().neq('id', 0).execute()
                    result = supabase_client.table(table_name).insert(batch).execute()
                
                print(f"Successfully uploaded batch {i//batch_size + 1} to {table_name}")
                
            except Exception as batch_error:
                print(f"Error uploading batch {i//batch_size + 1} to {table_name}: {batch_error}")
                continue
                
        print(f"Completed upload to {table_name}")
        
    except Exception as e:
        print(f"Error uploading to {table_name}: {e}")

def insert_table_data(table_name, data):
    for record in data:
        try:
            supabase_client.from_(table_name).insert(record).execute()
        except Exception as e:
            print(f"Error inserting record into {table_name}: {e}")

def delete_table_data(table_name):
    supabase_client.from_(table_name).delete().neq('Razon Social', None).execute()

def delete_resumen_contable_total(table_name):
    supabase_client.from_(table_name).delete().neq('mes', None).execute()

ids_empresas = pd.read_excel('data/cuits.xlsx')
cuit_to_name = dict(zip(ids_empresas['cuit'].astype(str), ids_empresas['razon_social']))

#Procesa CSV descomprimidos
csv_files = os.listdir('data\\historico_raw\\unzipped')
csv_files = [file for file in csv_files if file.endswith('.csv')]

# Regular expression to capture CUIT numbers
cuit_pattern = re.compile(r'_(\d{11})_')
cuit_numbers = [match.group(1) for file in csv_files if (match := cuit_pattern.search(file))]
company_names = [cuit_to_name.get(cuit) for cuit in cuit_numbers]

comprobantes_dfs = []
error_log = []  # List to store problematic files
for csv_file in csv_files:
    match = cuit_pattern.search(csv_file)
    if match:
        cuit = match.group(1)
        company_name = cuit_to_name.get(cuit)
        if company_name:
            try:
                # Try reading with default engine, fallback to python engine if error
                try:
                    data = pd.read_csv(
                        os.path.join('data\\historico_raw\\unzipped', csv_file),
                        sep=";",
                        on_bad_lines='skip'  # Skip bad lines
                    )
                except pd.errors.ParserError:
                    data = pd.read_csv(
                        os.path.join('data\\historico_raw\\unzipped', csv_file),
                        sep=";",
                        engine="python",
                        on_bad_lines='skip'  # Skip bad lines
                    )
                data['Razon Social'] = company_name
                if 'emitidos' in csv_file.lower():
                    data['Base'] = 'Emitidos'
                elif 'recibidos' in csv_file.lower():
                    data['Base'] = 'Recibidos'
                comprobantes_dfs.append(data)
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
                error_log.append(csv_file)
        else:
            print(f'No company name found for CUIT: {cuit}')

# Log problematic files to a text file for further inspection
if error_log:
    with open('data/error_log.txt', 'w') as log_file:
        log_file.write("\n".join(error_log))

comprobantes = pd.concat(comprobantes_dfs, ignore_index=True)

comprobantes['Empresa'] = comprobantes['Denominación Receptor'].fillna(comprobantes['Denominación Emisor']).str.strip().str.title().fillna("-")

comprobantes = comprobantes[['Fecha de Emisión', 'Tipo de Comprobante', 'Punto de Venta',
       'Número Desde', 'Número Hasta', 'Cód. Autorización',
       'Tipo Doc. Receptor', 'Nro. Doc. Receptor', 'Denominación Receptor',
       'Tipo Cambio', 'Moneda',  'Imp. Neto Gravado Total', 'Imp. Neto No Gravado', 
       'Imp. Op. Exentas', 'Total IVA', 'Imp. Total', 'Razon Social', 'Base',
       'Tipo Doc. Emisor', 'Nro. Doc. Emisor', 'Denominación Emisor',
       'Empresa']]

comprobantes = comprobantes.rename(columns={
    'Imp. Neto Gravado Total': 'Neto Gravado',
    'Imp. Neto No Gravado': 'Neto No Gravado',
    'Imp. Op. Exentas': 'Op. Exentas',
    'Total IVA': 'IVA'})

def format_number(x):
    return str(x).replace(",", ".") if pd.notnull(x) else x

for column in ['Neto Gravado', 'Neto No Gravado', 'Op. Exentas', 'IVA', 'Tipo Cambio', 'Imp. Total']:
    comprobantes[column] = comprobantes[column].apply(format_number).astype(float).fillna(0).round(0).astype(int)
comprobantes['Neto'] = comprobantes['Neto Gravado'] + comprobantes['Neto No Gravado'] + comprobantes['Op. Exentas'] 

sociedad_replacements = ["S.A.", "Srl", "Sociedad Anonima", "Company S A C", "S. R. L."]
for replacement in sociedad_replacements:
    comprobantes['Razon Social'] = comprobantes['Razon Social'].str.replace(replacement, '', regex=False).str.strip()

comprobantes = comprobantes[['Fecha de Emisión', 'Base', 'Tipo de Comprobante', 
    'Número Desde', 'Tipo Cambio', 'Moneda', 'Neto Gravado', 'Neto No Gravado',
    'Op. Exentas', 'IVA', 'Imp. Total', 'Razon Social', 'Empresa']]

# Notas de credito
comprobantes.loc[comprobantes['Tipo de Comprobante'] == 3, ['Neto Gravado', 'Neto No Gravado', 'Op. Exentas', 'IVA']] *= -1
comprobantes.loc[comprobantes['Tipo de Comprobante'] == 8, ['Neto Gravado', 'Neto No Gravado', 'Op. Exentas', 'IVA']] *= -1
# Factura C
comprobantes.loc[comprobantes['Tipo de Comprobante'] == 11, 'Neto No Gravado'] = comprobantes.loc[comprobantes['Tipo de Comprobante'] == 11, 'Imp. Total']

for column in ['Neto Gravado', 'Neto No Gravado', 'Op. Exentas', 'IVA', 'Imp. Total']:
    comprobantes.loc[comprobantes['Moneda'].str.contains('USD|DOL'), column] *= comprobantes.loc[comprobantes['Moneda'].str.contains('USD|DOL'), 'Tipo Cambio']

comprobantes['Neto'] = comprobantes['Neto Gravado'] + comprobantes['Neto No Gravado'] + comprobantes['Op. Exentas']

comprobantes['Empresa'] = comprobantes['Empresa'].fillna("-")

# Normaliza fechas con formato DD/MM/YYYY o D/M/YYYY a YYYY-MM-DD
def normalize_fecha_emision(fecha):
    if pd.isnull(fecha):
        return fecha
    # Si ya está en formato YYYY-MM-DD, no cambia
    if re.match(r'^\d{4}-\d{2}-\d{2}$', str(fecha)):
        return fecha
    # Si está en formato D/M/YYYY o DD/MM/YYYY
    match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', str(fecha))
    if match:
        d, m, y = match.groups()
        return f"{y}-{int(m):02d}-{int(d):02d}"
    return fecha

comprobantes['Fecha de Emisión'] = comprobantes['Fecha de Emisión'].apply(normalize_fecha_emision)
comprobantes['Fecha de Emisión'] = pd.to_datetime(comprobantes['Fecha de Emisión'], format='%Y-%m-%d', errors='coerce')
comprobantes['Mes'] = comprobantes['Fecha de Emisión'].dt.strftime('%Y-%m')
comprobantes['Fecha'] = comprobantes['Fecha de Emisión'].dt.strftime('%d/%m/%Y')

codigos_tipos_comprobante = pd.read_excel('codigos_tipos_comprobante.xls')
codigos_tipos_comprobante['Descripción'] = codigos_tipos_comprobante['Descripción'].str.title()
codigos_tipos_comprobante = codigos_tipos_comprobante.rename(columns={'Código': 'Tipo de Comprobante', 'Descripción': 'Tipo'})

# Reemplaza los valores de 'Tipo de Comprobante' por la descripción usando 'Código' como clave
comprobantes = comprobantes.merge(
    codigos_tipos_comprobante,
    on='Tipo de Comprobante',
    how='left'
)

comprobantes = comprobantes[['Fecha', 'Empresa', 'Tipo', 'Número Desde',
        'Neto Gravado', 'Neto No Gravado', 'Op. Exentas', 'IVA',
       'Neto', 'Imp. Total', 'Mes', 'Razon Social', 'Base']]


emitidos_historico = comprobantes[comprobantes['Base'] == 'Emitidos'].drop(columns=['Base'])
recibidos_historico = comprobantes[comprobantes['Base'] == 'Recibidos'].drop(columns=['Base'])

### Sacar datos para graficos

ventas_por_empresa = emitidos_historico.groupby(['Razon Social', 'Mes']).agg({
    'Neto Gravado': 'sum', 
    'Neto No Gravado': 'sum',
    'Op. Exentas': 'sum',
    'Neto': 'sum', 
    'IVA': 'sum', 
    'Imp. Total': 'sum'
}).reset_index()

ventas_por_empresa_cliente = emitidos_historico.groupby(['Razon Social', 'Empresa', 'Mes']).agg({
    'Neto Gravado': 'sum', 
    'Neto No Gravado': 'sum',
    'Op. Exentas': 'sum',
    'Neto': 'sum', 
    'IVA': 'sum',
    'Imp. Total': 'sum'
}).reset_index()

compras_por_empresa = recibidos_historico.groupby(['Razon Social', 'Mes']).agg({
    'Neto Gravado': 'sum', 
    'Neto No Gravado': 'sum',
    'Op. Exentas': 'sum',
    'Neto': 'sum', 
    'IVA': 'sum',
    'Imp. Total': 'sum'
}).reset_index()

compras_por_empresa_proveedor = recibidos_historico.groupby(['Razon Social', 'Empresa', 'Mes']).agg({
    'Neto Gravado': 'sum', 
    'Neto No Gravado': 'sum',
    'Op. Exentas': 'sum',
    'Neto': 'sum', 
    'IVA': 'sum',
    'Imp. Total': 'sum'
}).reset_index()

comprobantes_historico = ventas_por_empresa.merge(compras_por_empresa, on=['Razon Social', 'Mes'], how='left', suffixes=(' Ventas', ' Compras'))
numeric_columns = ['Neto Gravado Ventas', 'Neto No Gravado Ventas', 'Op. Exentas Ventas', 'Neto Ventas', 'IVA Ventas', 'Imp. Total Ventas', 'Neto Gravado Compras', 'Neto No Gravado Compras', 'Op. Exentas Compras', 'Neto Compras', 'IVA Compras', 'Imp. Total Compras']
comprobantes_historico[numeric_columns] = comprobantes_historico[numeric_columns].fillna(0).round(0).astype(int)
comprobantes_historico['Saldo IVA'] = comprobantes_historico['IVA Ventas'] - comprobantes_historico['IVA Compras']

# Melt the DataFrame to reshape it
comprobantes_historicos = comprobantes_historico.melt(
    id_vars=['Razon Social', 'Mes'], 
    value_vars=['Neto Ventas', 'IVA Ventas', 'Imp. Total Ventas', 'Neto Compras', 'IVA Compras', 'Imp. Total Compras', 'Saldo IVA'],
    var_name='Variable', 
    value_name='Monto'
)

# Ver clientes activos segun operaciones en ultimos 3 meses
ventas_por_empresa_cliente_activo = ventas_por_empresa_cliente.copy()
ventas_por_empresa_cliente_activo['Mes'] = pd.to_datetime(ventas_por_empresa_cliente_activo['Mes'], format='%Y-%m')
last_month = ventas_por_empresa_cliente_activo['Mes'].max()
three_months = [last_month - pd.DateOffset(months=i) for i in range(3)]
three_months_str = [m.strftime('%Y-%m') for m in three_months]

def is_active(group):
    active = group['Mes'].dt.strftime('%Y-%m').isin(three_months_str).any()
    return pd.Series({
        'Razon Social': group['Razon Social'].iloc[0],
        'Empresa': group['Empresa'].iloc[0],
        'cliente_activo': 'Si' if active else 'No',
        'mes_corriente': last_month.strftime('%Y-%m')
    })

active_clients = ventas_por_empresa_cliente_activo.groupby(['Razon Social', 'Empresa']).apply(is_active).reset_index(drop=True)

emitidos_historico.to_csv('data/emitidos_historico.csv', index=False)
recibidos_historico.to_csv('data/recibidos_historico.csv', index=False)
comprobantes_historicos.to_csv('data/comprobantes_historicos.csv', index=False)
ventas_por_empresa.to_csv('data/ventas_historico_mensual.csv', index=False)
compras_por_empresa.to_csv('data/compras_historico_mensual.csv', index=False)
ventas_por_empresa_cliente.to_csv('data/ventas_historico_cliente.csv', index=False)
compras_por_empresa_proveedor.to_csv('data/compras_historico_proveedor.csv', index=False)
active_clients.to_csv('data/clientes_activos.csv', index=False)



# Upload data to Supabase database
print("Starting database upload...")
delete_table_data('emitidos_historico')
upload_dataframe_to_supabase(emitidos_historico, 'emitidos_historico')
delete_table_data('recibidos_historico')
upload_dataframe_to_supabase(recibidos_historico, 'recibidos_historico')
delete_table_data('comprobantes_historicos')
upload_dataframe_to_supabase(comprobantes_historicos, 'comprobantes_historicos')
delete_table_data('ventas_historico_mensual')
upload_dataframe_to_supabase(ventas_por_empresa, 'ventas_historico_mensual')
delete_table_data('compras_historico_mensual')
upload_dataframe_to_supabase(compras_por_empresa, 'compras_historico_mensual')
delete_table_data('ventas_historico_cliente')
upload_dataframe_to_supabase(ventas_por_empresa_cliente, 'ventas_historico_cliente')
delete_table_data('compras_historico_proveedor')
upload_dataframe_to_supabase(compras_por_empresa_proveedor, 'compras_historico_proveedor')
delete_table_data('clientes_activos')
upload_dataframe_to_supabase(active_clients, 'clientes_activos')
print("Database upload completed!")



# -*- coding: utf-8 -*-
"""
INGRESAR MES A MANO

Genera tabla resumen sobre mes vencido en base a datos descargados y procesados en data/emitidos_historico.csv
Ver si es posible mejorarlo integrando descarga y procesamiento en este repositorio
"""
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
# Detect previous month automatically
today = datetime.now()
prev_month = today - relativedelta(months=1)
mes = prev_month.strftime("%m/%Y")  # Format as MM/YYYY

# Load data
cuits = pd.read_excel('C:\\Users\\facun\\OneDrive\\Documentos\\GitHub\\resumen_contable\\cuits.xlsx')
emitidos = emitidos_historico.copy()
emitidos = emitidos[emitidos['Fecha'].str.endswith(mes)]
recibidos = recibidos_historico.copy()
recibidos = recibidos[recibidos['Fecha'].str.endswith(mes)]

emitidos.to_csv('data/emitidos_mes_vencido.csv', index=False)
delete_table_data('emitidos_mes_vencido')
upload_dataframe_to_supabase(emitidos, 'emitidos_mes_vencido')

recibidos.to_csv('data/recibidos_mes_vencido.csv', index=False)
delete_table_data('recibidos_mes_vencido')
upload_dataframe_to_supabase(recibidos, 'recibidos_mes_vencido')

emitidos_por_empresa = emitidos.groupby(['Razon Social', 'Empresa']).agg({
    'Neto Gravado': 'sum',
    'Neto No Gravado': 'sum',
    'Op. Exentas': 'sum',
    'Neto': 'sum', 
    'IVA': 'sum', 
}).reset_index()
emitidos_por_empresa['Imp. Total'] = emitidos_por_empresa['Neto'] + emitidos_por_empresa['IVA']
emitidos_por_empresa = emitidos_por_empresa.sort_values('Neto', ascending=False)
emitidos_por_empresa.to_csv('data/emitidos_por_empresa_mes_vencido.csv', index=False)
delete_table_data('emitidos_por_empresa_mes_vencido')
upload_dataframe_to_supabase(emitidos_por_empresa, 'emitidos_por_empresa_mes_vencido')

#Recibidos por Proveedor
recibidos['Neto'] = recibidos['Neto Gravado'] + recibidos['Neto No Gravado'] + recibidos['Op. Exentas']
recibidos_por_empresa = recibidos.groupby(['Razon Social', 'Empresa']).agg({
    'Neto Gravado': 'sum',
    'Neto No Gravado': 'sum',
    'Op. Exentas': 'sum',
    'Neto': 'sum', 
    'IVA': 'sum', 
}).reset_index()
recibidos_por_empresa['Imp. Total'] = recibidos_por_empresa['Neto'] + recibidos_por_empresa['IVA']
recibidos_por_empresa = recibidos_por_empresa.sort_values('Imp. Total', ascending=False)
recibidos_por_empresa.to_csv('data/recibidos_por_empresa_mes_vencido.csv', index=False)
delete_table_data('recibidos_por_empresa_mes_vencido')
upload_dataframe_to_supabase(recibidos_por_empresa, 'recibidos_por_empresa_mes_vencido')

# IVA 
ventas_netas_df = emitidos.groupby('Razon Social')['Neto'].sum().reset_index()
compras_netas_df = recibidos.groupby('Razon Social')['Neto'].sum().reset_index()
ventas_netas_df = ventas_netas_df.rename(columns={'Neto': 'Ventas Netas'})
compras_netas_df = compras_netas_df.rename(columns={'Neto': 'Compras Netas'})
iva_ventas_df = emitidos.groupby('Razon Social')['IVA'].sum().reset_index()
iva_compras_df = recibidos.groupby('Razon Social')['IVA'].sum().reset_index()
iva_ventas_df = iva_ventas_df.rename(columns={'IVA': 'IVA Ventas'})
iva_compras_df = iva_compras_df.rename(columns={'IVA': 'IVA Compras'})
iva_df = pd.merge(iva_ventas_df, iva_compras_df, on='Razon Social', how='outer')
iva_df = iva_df.fillna(0)
iva_df['Saldo IVA'] = iva_df['IVA Compras'] - iva_df['IVA Ventas']

ventas_netas = ventas_netas_df.set_index('Razon Social')['Ventas Netas']
compras_netas = compras_netas_df.set_index('Razon Social')['Compras Netas']
iva_ventas = iva_df.set_index('Razon Social')['IVA Ventas']
iva_compras = iva_df.set_index('Razon Social')['IVA Compras']
saldo_iva = iva_df.set_index('Razon Social')['Saldo IVA']
# Ingresos Brutos

# Map values from cuits to emitidos
cuits.rename(columns={'razon_social': 'Razon Social'}, inplace=True)
sociedad_replacements = ["S.A.", "Srl", "Sociedad Anonima", "Company S A C", "S. R. L."]
for replacement in sociedad_replacements:
    cuits['Razon Social'] = cuits['Razon Social'].str.replace(replacement, '', regex=False).str.strip()

# Set 'Razon Social' as index for mapping
cuits_indexed = cuits.set_index('Razon Social')

for col in ['iib_bsas', 'alic_bsas', 'iib_caba', 'alic_caba', 'iib_salta', 'alic_salta', 'iib_otros', 'alic_otros']:
    emitidos[col.replace('iib', 'iibb')] = emitidos['Razon Social'].map(cuits_indexed[col] if col in cuits_indexed else None)

# List of columns to fill NaN values with zero
columns_to_fill = [
    'iibb_bsas',
    'alic_bsas',
    'iibb_caba',
    'alic_caba',
    'iibb_salta',
    'alic_salta',
    'iibb_otros',
    'alic_otros',
    'Neto'
]
# Fill NaN values with zero for the specified columns
emitidos[columns_to_fill] = emitidos[columns_to_fill].fillna(0)
emitidos['Ingresos Brutos'] = (emitidos['Neto'] * emitidos['iibb_bsas'] * emitidos['alic_bsas'] + 
                            emitidos['Neto'] * emitidos['iibb_caba'] * emitidos['alic_caba'] + 
                            emitidos['Neto'] * emitidos['iibb_salta'] * emitidos['alic_salta'] + 
                            emitidos['Neto'] * emitidos['iibb_otros'] * emitidos['alic_otros'])
ingresos_brutos = emitidos.groupby('Razon Social')['Ingresos Brutos'].sum().astype(int)

# Combine all indicators into a single DataFrame
indicators = pd.DataFrame({
    'Ventas Netas': ventas_netas,
    'Compras Netas': compras_netas,
    'IVA Ventas': iva_ventas,
    'IVA Compras': iva_compras,
    'Saldo IVA': saldo_iva,
    'Ingresos Brutos': ingresos_brutos,
}).reset_index()
indicators = indicators.rename(columns={'Razon Social': 'Company Name'})  
indicators['Mes'] = mes
indicators = indicators.melt(id_vars=['Company Name', 'Mes'], var_name='Variable', value_name='Value')
indicators['Value'] = indicators['Value'].fillna(0)
indicators['Value'] = indicators['Value'].astype(int)

indicators = indicators[indicators['Company Name'] != 'Unknown Company']

datos_pivot = indicators.pivot(index='Company Name', columns='Variable', values='Value')
datos_pivot = datos_pivot.reset_index()
datos_pivot = datos_pivot[['Company Name', 'Ventas Netas', 'Compras Netas', 'Saldo IVA', 'Ingresos Brutos']]
datos_pivot.columns = ['Razon Social', 'Vtas. Netas', 'Compras Netas', 'Saldo IVA', 'II.BB.']

# Clean the 'Razon Social' column by removing specified substrings
sociedad_replacements = ["S.A.", "Srl", "Sociedad Anonima", "Company S A C", "S. R. L."]
for replacement in sociedad_replacements:
    datos_pivot['Razon Social'] = datos_pivot['Razon Social'].str.replace(replacement, '', regex=False).str.strip()

current_date = datetime.now().strftime("%d-%m-%Y")

datos_pivot.to_csv('data/resumen_contable_mes_vencido.csv', index=False)

# Sum all columns except 'Razon Social'
totals = datos_pivot.drop('Razon Social', axis=1).sum().to_frame().T

totals.to_csv('data/resumen_contable_total.csv', index=False)

# Prepare data for database upload
# Add mes and fecha_generacion columns for database storage
datos_pivot_db = datos_pivot.copy()
datos_pivot_db['mes'] = mes
datos_pivot_db['fecha_generacion'] = datetime.now().strftime("%Y-%m-%d")

totals_db = totals.copy()
totals_db['mes'] = mes
totals_db['fecha_generacion'] = datetime.now().strftime("%Y-%m-%d")

# Upload to Supabase database
print("Uploading resumen contable data to database...")
delete_table_data('resumen_contable_mes_vencido')
upload_dataframe_to_supabase(datos_pivot_db, 'resumen_contable_mes_vencido')
delete_resumen_contable_total('resumen_contable_total')
upload_dataframe_to_supabase(totals_db, 'resumen_contable_total')
print("Resumen contable data uploaded to database!")

print('Terminando')
with open('data/leyenda_resumen_contable_mes_vencido.txt', 'w', encoding='utf-8') as file:
    file.write(f"Resumen Contable generado el {current_date} para el {mes}")