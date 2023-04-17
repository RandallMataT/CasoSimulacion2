import os
import paramiko
import datetime
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Definir variables de conexión
hostname = 'SistemasOperativos1'
port = 84
username = 'Randall'
password = '123'

# Se realiza la conexión con el servidor B
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=hostname, port=port, username=username, password=password)

# Se define el directorio en el servidor B donde se buscarán los archivos
remote_dir = 'C:\Users\Randall\VirtualBox VMs\Sis Operativo 1\Snapshots'

# Se crea una variable con la cantidad de dias exitentes de los archivos
days = 7

# Obtener la fecha actual
now = datetime.datetime.now()

# Restar los días deseados a la fecha actual para obtener la fecha límite para la búsqueda
delta = datetime.timedelta(days=days)
limit_date = now - delta

# Obtener una lista de los archivos en el directorio remoto que cumplen con los criterios de búsqueda
files = []
stdin, stdout, stderr = ssh_client.exec_command(f'find {remote_dir} -name ".log" -o -name ".txt" -type f -mtime +{days}')
for line in stdout:
    files.append(line.strip())

# Comprimir los archivos seleccionados
backup_filename = f'backup_{now.strftime("%Y-%m-%d_%H-%M-%S")}.zip'
with zipfile.ZipFile(backup_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    for file in files:
        file_basename = os.path.basename(file)
        zip_file.write(file, file_basename)

# Crear una carpeta segura en el servidor A
local_dir = 'C:\Users\Randall\VirtualBox VMs\WindowsServer\Snapshots'
if not os.path.exists(local_dir):
    os.makedirs(local_dir)

# Descargar el archivo comprimido en el servidor A
sftp_client = ssh_client.open_sftp()
sftp_client.get(backup_filename, os.path.join(local_dir, backup_filename))

# Verificar si el archivo descargado es el mismo que se comprimió
if os.path.getsize(os.path.join(local_dir, backup_filename)) == os.path.getsize(backup_filename):
    # Eliminar los archivos seleccionados en el servidor B
    for file in files:
        ssh_client.exec_command(f'rm {file}')

    # Crear un informe de respaldo exitoso
    body = 'El respaldo se realizó de forma exitosa'
else:
    # Crear un informe de error en el respaldo
    body = 'Hubo un error al realizar el respaldo'

# Cerrar la conexión con el servidor B
ssh_client.close()

# Enviar un correo electrónico con el informe
sender = 'randallmata2002@gmail.com'
receiver = 'rmata00047@ufide.ac.cr'
password = '1234'

message = MIMEMultipart()
message['Subject'] = 'Informe de respaldo'
message['From'] = sender
message['To'] = receiver

text = MIMEText(body)
message.attach(text)


