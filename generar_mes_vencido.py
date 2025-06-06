# -*- coding: utf-8 -*-
"""
INGRESAR MES A MANO

Genera tabla resumen sobre mes corriente en base a datos descargados y procesados en carpeta comprobantes_afip_vencido
Ver si es posible mejorarlo integrando descarga y procesamiento en este repositorio
"""
from datetime import datetime
import pandas as pd
mes = "05/2025"                                        ##### <- IGRESAR MES A MANO
#Abro datos
cuits  = pd.read_excel('C:\\Users\\facun\\OneDrive\\Documentos\\GitHub\\resumen_contable\\cuits.xlsx') 
emitidos = pd.read_csv('data/emitidos_historico.csv')
emitidos = emitidos[emitidos['Fecha'].str.endswith(mes)]
recibidos = pd.read_csv('data/recibidos_historico.csv')
recibidos = recibidos[recibidos['Fecha'].str.endswith(mes)]

emitidos = emitidos[['Fecha', 'Tipo', 'Nro.', 'Empresa', 'Neto', 'IVA', 'Razon Social']]
emitidos.to_csv('data/emitidos_mes_vencido.csv', index=False)


emitidos_por_empresa = emitidos.groupby(['Razon Social', 'Empresa']).agg({
    'Neto': 'sum', 
    'IVA': 'sum', 
}).reset_index()
emitidos_por_empresa['Imp. Total'] = emitidos_por_empresa['Neto'] + emitidos_por_empresa['IVA']
emitidos_por_empresa = emitidos_por_empresa.sort_values('Neto', ascending=False)
emitidos_por_empresa.rename(columns={'Razon Social': 'Sociedad'}, inplace=True)
emitidos_por_empresa.to_csv('data/emitidos_por_empresa_mes_vencido.csv', index=False)

#Recibidos por Proveedor
recibidos['Neto'] = recibidos['Neto Gravado'] + recibidos['Neto No Gravado'] + recibidos['Op. Exentas']
recibidos = recibidos[['Fecha', 'Tipo', 'Nro.', 'Empresa', 'Neto', 'IVA', 'Razon Social']]
recibidos.to_csv('data/recibidos_mes_vencido.csv', index=False)
recibidos_por_empresa = recibidos.groupby(['Razon Social', 'Empresa']).agg({
    'Neto': 'sum', 
    'IVA': 'sum', 
}).reset_index()
recibidos_por_empresa['Imp. Total'] = recibidos_por_empresa['Neto'] + recibidos_por_empresa['IVA']
recibidos_por_empresa = recibidos_por_empresa.sort_values('Imp. Total', ascending=False)
recibidos_por_empresa.rename(columns={'Razon Social': 'Sociedad'}, inplace=True)
recibidos_por_empresa.to_csv('data/recibidos_por_empresa_mes_vencido.csv', index=False)

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
# Cargas Sociales

ctas_tributarias = pd.read_excel('data/unified_cuentas_tributarias.xlsx')



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
datos_pivot.columns = ['Sociedad', 'Vtas. Netas', 'Compras Netas', 'Saldo IVA', 'II.BB.']

# Clean the 'Sociedad' column by removing specified substrings
sociedad_replacements = ["S.A.", "Srl", "Sociedad Anonima", "Company S A C", "S. R. L."]
for replacement in sociedad_replacements:
    datos_pivot['Sociedad'] = datos_pivot['Sociedad'].str.replace(replacement, '', regex=False).str.strip()

current_date = datetime.now().strftime("%d-%m-%Y")

datos_pivot.to_csv('data/resumen_contable_mes_vencido.csv', index=False)

# Sum all columns except 'Sociedad'
totals = datos_pivot.drop('Sociedad', axis=1).sum().to_frame().T

totals.to_csv('data/resumen_contable_total.csv', index=False)

with open('data/leyenda_resumen_contable_mes_vencido.txt', 'w', encoding='utf-8') as file:
    file.write(f"Resumen Contable al {current_date} para el mes corriente")