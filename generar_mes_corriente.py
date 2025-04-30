# -*- coding: utf-8 -*-
"""
Genera tabla resumen sobre mes corriente en base a datos descargados y procesados en carpeta comprobantes_afip_actual
Ver si es posible mejorarlo integrando descarga y procesamiento en este repositorio
"""
from datetime import datetime
import pandas as pd
mes = datetime.now().strftime("%m-%Y")
#Abro datos
cuits  = pd.read_excel('C:\\Users\\facun\\OneDrive\\Documentos\\GitHub\\comprobantes_afip_actual\\cuits.xlsx') 
emitidos = pd.read_csv('C:\\Users\\facun\\OneDrive\\Documentos\\GitHub\\comprobantes_afip_actual\\emitidos.csv')
recibidos =  pd.read_csv('C:\\Users\\facun\\OneDrive\\Documentos\\GitHub\\comprobantes_afip_actual\\recibidos.csv')

#Emitidos por Cliente
emitidos['Neto'] = emitidos['Imp. Neto Gravado'] + emitidos['Imp. Neto No Gravado'] + emitidos['Imp. Op. Exentas'] 
emitidos = emitidos[['Fecha', 'Tipo', 'Número Desde', 'Denominación Receptor', 'Neto', 'IVA', 'Imp. Total', 'razon_social']]
emitidos['Denominación Receptor'] = emitidos['Denominación Receptor'].str.strip().str.title()
sociedad_replacements = ["S.A.", "Srl", "Sociedad Anonima", "Company S A C", "S. R. L."]
for replacement in sociedad_replacements:
    emitidos['razon_social'] = emitidos['razon_social'].str.replace(replacement, '', regex=False).str.strip()
emitidos.to_csv('data/emitidos_mes_actual.csv', index=False)
ventas_netas = emitidos.groupby('razon_social')['Neto'].sum()
emitidos_por_empresa = emitidos.groupby(['razon_social', 'Denominación Receptor']).agg({
    'Neto': 'sum', 
    'IVA': 'sum', 
    'Imp. Total': 'sum'
}).reset_index()
emitidos_por_empresa = emitidos_por_empresa.sort_values('Imp. Total', ascending=False)
emitidos_por_empresa.rename(columns={'razon_social': 'Sociedad'}, inplace=True)
emitidos_por_empresa.to_csv('data/emitidos_por_empresa_mes_actual.csv', index=False)
#Recibidos por Proveedor
recibidos['Neto'] = recibidos['Imp. Neto Gravado'] + recibidos['Imp. Neto No Gravado'] + recibidos['Imp. Op. Exentas']
recibidos = recibidos[['Fecha', 'Tipo', 'Número Desde', 'Denominación Emisor', 'Neto', 'IVA', 'Imp. Total', 'razon_social']]
recibidos['Denominación Emisor'] = recibidos['Denominación Emisor'].str.strip().str.title()
sociedad_replacements = ["S.A.", "Srl", "Sociedad Anonima", "Company S A C", "S. R. L."]
for replacement in sociedad_replacements:
    recibidos['razon_social'] = recibidos['razon_social'].str.replace(replacement, '', regex=False).str.strip()
recibidos.to_csv('data/recibidos_mes_actual.csv', index=False)
recibidos_por_empresa = recibidos.groupby(['razon_social', 'Denominación Emisor']).agg({
    'Neto': 'sum', 
    'IVA': 'sum', 
    'Imp. Total': 'sum'
}).reset_index()
recibidos_por_empresa = recibidos_por_empresa.sort_values('Imp. Total', ascending=False)
recibidos_por_empresa.rename(columns={'razon_social': 'Sociedad'}, inplace=True)
recibidos_por_empresa.to_csv('data/recibidos_por_empresa_mes_actual.csv', index=False)


# IVA 
iva_ventas_df = emitidos.groupby('razon_social')['IVA'].sum().reset_index()
iva_compras_df = recibidos.groupby('razon_social')['IVA'].sum().reset_index()
iva_ventas_df = iva_ventas_df.rename(columns={'IVA': 'IVA Ventas'})
iva_compras_df = iva_compras_df.rename(columns={'IVA': 'IVA Compras'})
iva_df = pd.merge(iva_ventas_df, iva_compras_df, on='razon_social', how='outer')
iva_df = iva_df.fillna(0)
iva_df['Saldo IVA'] = iva_df['IVA Compras'] - iva_df['IVA Ventas']
iva_ventas = iva_df.set_index('razon_social')['IVA Ventas']
iva_compras = iva_df.set_index('razon_social')['IVA Compras']
saldo_iva = iva_df.set_index('razon_social')['Saldo IVA']
# Ingresos Brutos
cuits = cuits.set_index('razon_social')
emitidos['iibb_bsas'] = emitidos['razon_social'].map(cuits['iib_bsas'])
emitidos['alic_bsas'] = emitidos['razon_social'].map(cuits['alic_bsas'])
emitidos['iibb_caba'] = emitidos['razon_social'].map(cuits['iib_caba'])
emitidos['alic_caba'] = emitidos['razon_social'].map(cuits['alic_caba'])
emitidos['iibb_salta'] = emitidos['razon_social'].map(cuits['iib_salta'])
emitidos['alic_salta'] = emitidos['razon_social'].map(cuits['alic_salta'])
emitidos['iibb_otros'] = emitidos['razon_social'].map(cuits['iib_otros'])
emitidos['alic_otros'] = emitidos['razon_social'].map(cuits['alic_otros'])
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
ingresos_brutos = emitidos.groupby('razon_social')['Ingresos Brutos'].sum().astype(int)
# Cargas Sociales

# Combine all indicators into a single DataFrame
indicators = pd.DataFrame({
    'Ventas Netas': ventas_netas,
    'IVA Ventas': iva_ventas,
    'IVA Compras': iva_compras,
    'Saldo IVA': saldo_iva,
    'Ingresos Brutos': ingresos_brutos,
}).reset_index()
# Merge with company names to get a complete view
indicators = indicators.rename(columns={'razon_social': 'Company Name'})  
indicators['Mes'] = mes
# Convert to tidy format (melt)
indicators = indicators.melt(id_vars=['Company Name', 'Mes'], var_name='Variable', value_name='Value')
# Handle NaN values by filling with 0
indicators['Value'] = indicators['Value'].fillna(0)
# Convert 'Value' column to integer
indicators['Value'] = indicators['Value'].astype(int)

indicators = indicators[indicators['Company Name'] != 'Unknown Company']

datos_pivot = indicators.pivot(index='Company Name', columns='Variable', values='Value')

datos_pivot = datos_pivot.reset_index()

datos_pivot = datos_pivot[['Company Name', 'Ventas Netas', 'Saldo IVA', 'Ingresos Brutos']]

datos_pivot.columns = ['Sociedad', 'Vtas. Netas', 'Saldo IVA', 'II.BB.']

# Clean the 'Sociedad' column by removing specified substrings
sociedad_replacements = ["S.A.", "Srl", "Sociedad Anonima", "Company S A C", "S. R. L."]
for replacement in sociedad_replacements:
    datos_pivot['Sociedad'] = datos_pivot['Sociedad'].str.replace(replacement, '', regex=False).str.strip()

current_date = datetime.now().strftime("%d-%m-%Y")

datos_pivot.to_csv('data/resumen_contable_mes_actual.csv', index=False)

with open('data/leyenda_resumen_contable_mes_actual.txt', 'w', encoding='utf-8') as file:
    file.write(f"Resumen Contable al {current_date} para el mes corriente")