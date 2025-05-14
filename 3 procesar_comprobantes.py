"""
Procesamiento de csv ya descomprimidos
"""

import os
import pandas as pd
import re
import time
import shutil
import zipfile

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
                data = pd.read_csv(os.path.join('data\\historico_raw\\unzipped', csv_file), sep=";")
                data['Razon Social'] = company_name
                if 'emitidos' in csv_file.lower():
                    data['Base'] = 'Emitidos'
                elif 'recibidos' in csv_file.lower():
                    data['Base'] = 'Recibidos'
                comprobantes_dfs.append(data)
            except pd.errors.ParserError as e:
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


def format_number(x):
    return str(x).replace(",", ".") if pd.notnull(x) else x

for column in ['Imp. Neto Gravado', 'Imp. Neto No Gravado', 'Imp. Op. Exentas', 'IVA', 'Tipo Cambio', 'Imp. Total']:
    comprobantes[column] = comprobantes[column].apply(format_number).astype(float).fillna(0).round(0).astype(int)
comprobantes['Neto'] = comprobantes['Imp. Neto Gravado'] + comprobantes['Imp. Neto No Gravado'] + comprobantes['Imp. Op. Exentas'] 

sociedad_replacements = ["S.A.", "Srl", "Sociedad Anonima", "Company S A C", "S. R. L."]
for replacement in sociedad_replacements:
    comprobantes['Razon Social'] = comprobantes['Razon Social'].str.replace(replacement, '', regex=False).str.strip()

comprobantes = comprobantes[['Fecha de Emisión', 'Base', 'Tipo de Comprobante', 
    'Número Desde', 'Tipo Cambio', 'Moneda', 'Imp. Neto Gravado', 'Imp. Neto No Gravado',
    'Imp. Op. Exentas', 'IVA', 'Imp. Total', 'Razon Social', 'Empresa']]

# Notas de credito
comprobantes.loc[comprobantes['Tipo de Comprobante'] == 3, ['Imp. Neto Gravado', 'Imp. Neto No Gravado', 'Imp. Op. Exentas', 'IVA']] *= -1
comprobantes.loc[comprobantes['Tipo de Comprobante'] == 8, ['Imp. Neto Gravado', 'Imp. Neto No Gravado', 'Imp. Op. Exentas', 'IVA']] *= -1
# Factura C
comprobantes.loc[comprobantes['Tipo de Comprobante'] == 11, 'Imp. Neto No Gravado'] = comprobantes.loc[comprobantes['Tipo de Comprobante'] == 11, 'Imp. Total']

for column in ['Imp. Neto Gravado', 'Imp. Neto No Gravado', 'Imp. Op. Exentas', 'IVA']:
    comprobantes.loc[comprobantes['Moneda'].str.contains('USD|DOL'), column] *= comprobantes.loc[comprobantes['Moneda'].str.contains('USD|DOL'), 'Tipo Cambio']

comprobantes['Neto'] = comprobantes['Imp. Neto Gravado'] + comprobantes['Imp. Neto No Gravado'] + comprobantes['Imp. Op. Exentas']

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
        'Imp. Neto Gravado', 'Imp. Neto No Gravado', 'Imp. Op. Exentas', 'IVA',
       'Neto', 'Imp. Total', 'Mes', 'Razon Social', 'Base']]

comprobantes = comprobantes.rename(columns={
    'Número Desde': 'Nro.', })

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
comprobantes_historico['Saldo IVA'] = comprobantes_historico['IVA Ventas'] - comprobantes_historico['IVA Compras']

# Melt the DataFrame to reshape it
comprobantes_historicos = comprobantes_historico.melt(
    id_vars=['Razon Social', 'Mes'], 
    value_vars=['Neto Ventas', 'IVA Ventas', 'Neto Compras', 'IVA Compras', 'Saldo IVA'],
    var_name='Variable', 
    value_name='Monto'
)



emitidos_historico.to_csv('data/emitidos_historico.csv', index=False)
recibidos_historico.to_csv('data/recibidos_historico.csv', index=False)



# Guardar los DataFrames en CSV
comprobantes_historicos.to_csv('data/comprobantes_historicos.csv', index=False)
ventas_por_empresa.to_csv('data/ventas_historico_mensual.csv', index=False)
compras_por_empresa.to_csv('data/compras_historico_mensual.csv', index=False)
ventas_por_empresa_cliente.to_csv('data/ventas_historico_cliente.csv', index=False)
compras_por_empresa_proveedor.to_csv('data/compras_historico_proveedor.csv', index=False)
