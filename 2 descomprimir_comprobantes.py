
import os
import pandas as pd
import zipfile

ids_empresas = pd.read_excel('data/cuits.xlsx')
cuit_to_name = dict(zip(ids_empresas['cuit'].astype(str), ids_empresas['razon_social']))

raw_dir = 'data\\historico_raw'
files = os.listdir(raw_dir)

#Descomprime archivos
csv_files = os.listdir(raw_dir)
csv_files_zip = [file for file in csv_files if file.endswith('.zip')]

# Define directories for 2024 and 2025
folders_to_process = ['2024', '2025']
unzipped_dir = os.path.join(raw_dir, 'unzipped')

# Ensure the unzipped directory exists
os.makedirs(unzipped_dir, exist_ok=True)

# Process ZIP files in 2024 and 2025 folders
for folder in folders_to_process:
    folder_path = os.path.join(raw_dir, folder)
    if os.path.exists(folder_path):
        zip_files = [file for file in os.listdir(folder_path) if file.endswith('.zip')]
        for zip_file in zip_files:
            zip_path = os.path.join(folder_path, zip_file)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(unzipped_dir)
                print(f'Extracted: {zip_file} from {folder}')

