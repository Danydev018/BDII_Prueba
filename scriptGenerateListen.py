import csv
import random
from datetime import datetime, timedelta

# Rutas de los archivos
users_file = "./csv/users.csv"
songs_file = "./csv/song.csv"

# Leer IDs de usuarios
with open(users_file, newline='', encoding='utf-8') as f:
    users = [row[0] for i, row in enumerate(csv.reader(f)) if i > 0]

# Leer IDs de canciones
with open(songs_file, newline='', encoding='utf-8') as f:
    songs = [row[0] for i, row in enumerate(csv.reader(f)) if i > 0]

# Generar 300 registros aleatorios
for _ in range(300):
    user_id = random.choice(users)
    song_id = random.choice(songs)
    # Fecha aleatoria en 2025
    start_date = datetime(2025, 1, 1)
    random_days = random.randint(0, 364)
    random_time = timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    fecha = (start_date + timedelta(days=random_days) + random_time).strftime("%Y-%m-%d %H:%M:00")
    print(f"{user_id},{song_id},{fecha}")