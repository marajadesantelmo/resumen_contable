# Importo paquetes
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from datetime import datetime
import time

# Seteo de driver

# #Marionette
print('Abriendo navegador Mozilla')
try:
    subprocess.Popen(['activar_mozilla.bat'])
    print("Navegador abierto exitosamente.")
except subprocess.CalledProcessError as e:
    print(f"Error occurred while executing the batch file: {e}")

time.sleep(2)
service = Service(executable_path="C:\\Users\\facun\\OneDrive\\Documentos\\GitHub\\comprobantes_afip_actual\\geckodriver.exe", port=3000, service_args=['--marionette-port', '2828', '--connect-existing'])
driver = webdriver.Firefox(service=service)
# driver.save_screenshot('screenshot.png')

# Función para obtener fechas del usuario

def obtener_fechas_usuario():
    while True:
        try:
            fecha_inicio = input("Ingrese la fecha de inicio (DD-MM-YYYY): ")
            fecha_fin = input("Ingrese la fecha de fin (DD-MM-YYYY): ")
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%d-%m-%Y')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%d-%m-%Y')
            if fecha_inicio_dt > fecha_fin_dt:
                raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")
            return fecha_inicio_dt.strftime('%d/%m/%Y'), fecha_fin_dt.strftime('%d/%m/%Y')
        except ValueError as e:
            print(f"Error: {e}. Por favor, intente nuevamente.")

fecha_inicio, fecha_fin = obtener_fechas_usuario()
rango_fechas = f"{fecha_inicio} - {fecha_fin}"
print("Ingresando clave y usuario AFIP")
driver.get('https://auth.afip.gob.ar/contribuyente_/login.xhtml')
input_cuit = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "F1:username")))
input_cuit.clear() 
time.sleep(1)
input_cuit.send_keys('23363457959') 
boton_siguiente = driver.find_element(By.XPATH, value='//*[@id="F1:btnSiguiente"]')
boton_siguiente.click()
time.sleep(2)
input_clave = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "F1:password")))
input_clave.send_keys('Maria299419')
time.sleep(1)
boton_ingresar = driver.find_element(By.XPATH, value='//*[@id="F1:btnIngresar"]')
boton_ingresar.click()
time.sleep(1)
print("Completando buscador de tramites y servicios con 'Mis Comprobantes'")
input_buscador = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "buscadorInput")))
input_buscador.send_keys('Mis Comprobantes')
boton_buscador = driver.find_element(By.XPATH, value='//*[@id="rbt-menu-item-0"]')
boton_buscador.click()
time.sleep(5)
driver.switch_to.window(driver.window_handles[1])
time.sleep(5)
for i in range(1, 17):
    try:
        print(f"Elijo empresa numero {i}")
        time.sleep(2)
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, f'/html/body/form/main/div/div/div[2]/div/div[{i}]/div/a/div/div[2]/h3')))
        boton = driver.find_element(By.XPATH, value=f'/html/body/form/main/div/div/div[2]/div/div[{i}]/div/a/div/div[2]/h3')
        driver.execute_script("arguments[0].scrollIntoView(true);", boton)
        boton.click()
    except TimeoutException:
        print("TimeoutException: No se pudo acceder a la selección de empresa")
    
    print("Yendo a Comprobantes Emitidos")
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnEmitidos"]')))
    boton_emitidos = driver.find_element(By.XPATH, value='//*[@id="btnEmitidos"]')
    boton_emitidos.click()
    print(f"Enviando el rango de fechas {rango_fechas}")
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'fechaEmision')))
    input_fechas = driver.find_element(By.ID, "fechaEmision")
    input_fechas.click()
    input_fechas.clear()
    input_fechas.send_keys(rango_fechas)
    driver.execute_script("window.scrollBy(0, window.innerHeight);")
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="buscarComprobantes"]')))
    boton_buscar = driver.find_element(By.XPATH, value='//*[@id="buscarComprobantes"]')
    boton_buscar.click()
    time.sleep(1)
    # Locate the button that contains the text 'CSV' and click it
    csv_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[span[text()='CSV']]"))
    )
    csv_button.click()
    time.sleep(5)
    print("Yendo a Comprobantes Recibidos")
    driver.back()
    time.sleep(3)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnRecibidos"]')))
    boton_recibidos = driver.find_element(By.XPATH, value='//*[@id="btnRecibidos"]')
    boton_recibidos.click()
    print(f"Enviando el rango de fechas {rango_fechas}")
    time.sleep(1)
    input_fechas = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'fechaEmision')))
    input_fechas.click()
    input_fechas.clear()
    input_fechas.send_keys(rango_fechas)
    time.sleep(1)
    driver.execute_script("window.scrollBy(0, window.innerHeight);")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="buscarComprobantes"]')))
    boton_buscar = driver.find_element(By.XPATH, value='//*[@id="buscarComprobantes"]')
    boton_buscar.click()
    time.sleep(6)
    csv_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[span[text()='CSV']]"))
    )
    csv_button.click()
    time.sleep(5)
    driver.back()
    time.sleep(1)
    driver.back()

driver.back()
time.sleep(10)
print('Descarga terminada')



