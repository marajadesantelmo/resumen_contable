"""
Script que genera emitidos_historico y recibidos_historico 
Primero cambia los nombres de los comprobantes descargados en 
'data\\historico_raw' y luego los procesa y los copia en historico_procesado.
"""

import os
import pandas as pd
import re
import time
import shutil
import zipfile

ids_empresas = pd.read_excel('data/cuits.xlsx')
cuit_to_name = dict(zip(ids_empresas['cuit'].astype(str), ids_empresas['razon_social']))

raw_dir = 'data\\historico_raw'
comprobantes_dir = 'data\\historico_procesado'
files = os.listdir(raw_dir)

#Procesamiento de XLSX
pattern = re.compile(r'Mis Comprobantes (Emitidos|Recibidos) - CUIT (\d+)\(\d+\)\.xlsx')
cuit_files = {cuit: {'Emitidos': False, 'Recibidos': False} for cuit in cuit_to_name}

for filename in files:
    match = pattern.match(filename)
    if match:
        tipo, cuit = match.groups()
        company_name = cuit_to_name.get(cuit)
        if company_name:
            new_filename = f"{tipo} - {company_name} - {cuit}.xlsx"
            old_filepath = os.path.join(raw_dir, filename)
            new_filepath = os.path.join(comprobantes_dir, new_filename)
            shutil.copy2(old_filepath, new_filepath)
            print(f'Copiado: {filename} -> {new_filename}')
            # Mark the file type as present for the CUIT
            cuit_files[cuit][tipo] = True
        else:
            print(f'No company name found for CUIT: {cuit}')

# Check if there are two files for each company
missing_files = []
for cuit, files in cuit_files.items():
    if not all(files.values()):
        company_name = cuit_to_name[cuit]
        missing_types = [key for key, value in files.items() if not value]
        missing_files.append((company_name, cuit, missing_types))

if missing_files:
    print('The following companies are missing files:')
    for company_name, cuit, missing_types in missing_files:
        print(f"{company_name} ({cuit}) is missing: {', '.join(missing_types)}")
else:
    print('All companies have both Emitidos and Recibidos files.')

print('Renaming and checking completed.')
time.sleep(10)


#Procesamiento de CSVs
csv_files = os.listdir(raw_dir)
csv_files_zip = [file for file in csv_files if file.endswith('.zip')]
# Extract all CSV files from the ZIP archives
for zip_file in csv_files_zip:
    zip_path = os.path.join(raw_dir, zip_file)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('data\\historico_raw\\unzipped')
        print(f'Extracted: {zip_file}')

csv_files = os.listdir('data\\historico_raw\\unzipped')
csv_files = [file for file in csv_files if file.endswith('.csv')]

# Regular expression to capture CUIT numbers
cuit_pattern = re.compile(r'_(\d{11})_')
cuit_numbers = [match.group(1) for file in csv_files if (match := cuit_pattern.search(file))]
company_names = [cuit_to_name.get(cuit) for cuit in cuit_numbers]

comprobantes_dfs = []
for csv_file in csv_files:
    match = cuit_pattern.search(csv_file)
    if match:
        cuit = match.group(1)
        company_name = cuit_to_name.get(cuit)
        if company_name:
            data = pd.read_csv(os.path.join('data\\historico_raw\\unzipped', csv_file), sep=";")
            data['Razon Social'] = company_name
            if 'emitidos' in csv_file.lower():
                data['Base'] = 'Emitidos'
            elif 'recibidos' in csv_file.lower():
                data['Base'] = 'Recibidos'
            comprobantes_dfs.append(data)
        else:
            print(f'No company name found for CUIT: {cuit}')

comprobantes = pd.concat(comprobantes_dfs, ignore_index=True)

comprobantes['Empresa'] = comprobantes['Denominación Receptor'].fillna(comprobantes['Denominación Emisor']).str.strip().str.title()

def format_number(x):
    return str(x).replace(",", ".") if pd.notnull(x) else x

for column in ['Imp. Neto Gravado', 'Imp. Neto No Gravado', 'Imp. Op. Exentas', 'IVA', 'Tipo Cambio']:
    comprobantes[column] = comprobantes[column].apply(format_number).astype(float).fillna(0).round(0).astype(int)
comprobantes['Neto'] = comprobantes['Imp. Neto Gravado'] + comprobantes['Imp. Neto No Gravado'] + comprobantes['Imp. Op. Exentas'] 

sociedad_replacements = ["S.A.", "Srl", "Sociedad Anonima", "Company S A C", "S. R. L."]
for replacement in sociedad_replacements:
    comprobantes['Razon Social'] = comprobantes['Razon Social'].str.replace(replacement, '', regex=False).str.strip()

comprobantes = comprobantes[['Fecha de Emisión', 'Base', 'Tipo de Comprobante', 
    'Número Desde', 'Tipo Cambio', 'Moneda', 'Imp. Neto Gravado', 'Imp. Neto No Gravado',
    'Imp. Op. Exentas', 'IVA', 'Razon Social', 'Empresa']]

comprobantes.loc[comprobantes['Tipo de Comprobante'] == 3, ['Imp. Neto Gravado', 'Imp. Neto No Gravado', 'Imp. Op. Exentas', 'IVA']] *= -1
comprobantes.loc[comprobantes['Tipo de Comprobante'] == 8, ['Imp. Neto Gravado', 'Imp. Neto No Gravado', 'Imp. Op. Exentas', 'IVA']] *= -1

for column in ['Imp. Neto Gravado', 'Imp. Neto No Gravado', 'Imp. Op. Exentas',  'IVA']:
    comprobantes.loc[comprobantes['Moneda'] == 'USD', column] *= comprobantes.loc[comprobantes['Moneda'] == 'USD', 'Tipo Cambio']

comprobantes['Neto'] = comprobantes['Imp. Neto Gravado'] + comprobantes['Imp. Neto No Gravado'] + comprobantes['Imp. Op. Exentas']

comprobantes['Empresa'] = comprobantes['Empresa'].fillna("-")
comprobantes['Fecha de Emisión'] = pd.to_datetime(comprobantes['Fecha de Emisión'])
comprobantes['Mes'] = comprobantes['Fecha de Emisión'].dt.strftime('%m-%Y')

emitidos_historico = comprobantes[comprobantes['Base'] == 'Emitidos'].drop(columns=['Base'])
recibidos_historico = comprobantes[comprobantes['Base'] == 'Recibidos'].drop(columns=['Base'])

### Sacar datos para graficos

ventas_por_empresa = emitidos_historico.groupby(['Razon Social', 'Mes']).agg({
    'Neto': 'sum', 
    'IVA': 'sum'
}).reset_index()

ventas_por_empresa_cliente = emitidos_historico.groupby(['Razon Social', 'Empresa', 'Mes']).agg({
    'Neto': 'sum', 
    'IVA': 'sum'
}).reset_index()

compras_por_empresa = recibidos_historico.groupby(['Razon Social', 'Mes']).agg({
    'Neto': 'sum', 
    'IVA': 'sum'
}).reset_index()

compras_por_empresa_proveedor = recibidos_historico.groupby(['Razon Social', 'Empresa', 'Mes']).agg({
    'Neto': 'sum', 
    'IVA': 'sum'
}).reset_index()

comprobantes_historico = ventas_por_empresa.merge(compras_por_empresa, on=['Razon Social', 'Mes'], how='left', suffixes=(' Ventas', ' Compras'))
# Round and convert numeric columns to integers
numeric_columns = ['Neto Ventas', 'IVA Ventas', 'Neto Compras', 'IVA Compras']
comprobantes_historico[numeric_columns] = comprobantes_historico[numeric_columns].fillna(0).round(0).astype(int)
# Guardar los DataFrames en CSV
comprobantes_historico.to_csv('data/comprobantes_historicos.csv', index=False)
ventas_por_empresa.to_csv('data/ventas_historico_mensual.csv', index=False)
compras_por_empresa.to_csv('data/compras_historico_mensual.csv', index=False)
ventas_por_empresa_cliente.to_csv('data/ventas_historico_cliente.csv', index=False)
compras_por_empresa_proveedor.to_csv('data/compras_historico_proveedor.csv', index=False)
