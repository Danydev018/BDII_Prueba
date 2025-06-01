import csv
from collections import defaultdict
from datetime import datetime

input_file = './csv/listen.csv'
output_file = './csv/canciones_escuchadas_por_mes.csv'

conteo = defaultdict(int)

with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cancion_id = row['cacion_id']
        fecha = row['fecha_escucha']
        dt = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
        key = (cancion_id, dt.year, dt.month)
        conteo[key] += 1

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['id_cancion', 'anio', 'mes', 'total_escuchadas'])
    for (cancion_id, anio, mes), total in sorted(conteo.items()):
        writer.writerow([cancion_id, anio, mes, total])

print(f'Archivo generado: {output_file}')