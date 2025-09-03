
import pandas as pd

comprobantes = pd.read_csv('data/emitidos_por_empresa_mes_vencido.csv')

dassa = comprobantes[(comprobantes['Sociedad']=='Deposito Avellaneda Sur')]

dassa['Neto'].sum()