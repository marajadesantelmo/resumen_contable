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
print('Cambiando nombre de comprobantes')
# Load the company IDs
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

emitidos_dfs = []
recididos_dfs = []

for csv_file in csv_files:
    match = cuit_pattern.search(csv_file)
    if match:
        cuit = match.group(1)
        company_name = cuit_to_name.get(cuit)
        if company_name:
            data = pd.read_csv(os.path.join('data\\historico_raw\\unzipped', csv_file), sep=";")
            data['Razon Social'] = company_name
            if 'emitidos' in csv_file.lower():
                emitidos_dfs.append(data)
            elif 'recibidos' in csv_file.lower():
                recididos_dfs.append(data)
        else:
            print(f'No company name found for CUIT: {cuit}')

emitidos = pd.concat(emitidos_dfs, ignore_index=True)
recibidos = pd.concat(recididos_dfs, ignore_index=True)


## Procesamiento de los datos

def format_number(x):
    return x.replace(",", "X").replace(".", ",") 

for column in ['Imp. Neto Gravado', 'Imp. Neto No Gravado', 'Imp. Op. Exentas', 'IVA', 'Imp. Total']:
    emitidos[column] = emitidos[column].apply(format_number)

emitidos['Neto'] = emitidos['Imp. Neto Gravado'] + emitidos['Imp. Neto No Gravado'] + emitidos['Imp. Op. Exentas'] 
emitidos = emitidos[['Fecha', 'Tipo', 'Número Desde', 'Denominación Receptor', 'Neto', 'IVA', 'Imp. Total', 'razon_social']]
emitidos['Denominación Receptor'] = emitidos['Denominación Receptor'].str.strip().str.title()




emitidos.columns