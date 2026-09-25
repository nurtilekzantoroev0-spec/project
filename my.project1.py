import sqlite3
import pandas as pd
conn = sqlite3.connect('demo.db')
cur = conn.cursor()

# DDL: создаём таблицы
cur.executescript("""
    CREATE TABLE IF NOT EXISTS passenger (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        city TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS pass_in_trip (
        trip_id INTEGER NOT NULL,
        passenger_id INTEGER NOT NULL,
        time_in TEXT NOT NULL,
        FOREIGN KEY (passenger_id) REFERENCES passenger(id)
    );
""")

# DML: вставляем данные
cur.executemany(
    "INSERT INTO passenger (name, city) VALUES (?, ?)",
    [("Alice", "Moscow"), ("Bob", "St. Petersburg"), ("Carol", "Kazan"), ("Dave", "Moscow")]
)

cur.executemany(
    "INSERT INTO pass_in_trip (trip_id, passenger_id, time_in) VALUES (?, ?, ?)",
    [
        (1, 1, "10:00"),
        (1, 2, "10:15"),
        (2, 3, "11:00"),
        (3, 4, "12:30"),
        (3, 1, "12:40")
    ]
)
conn.commit()
conn.close()

query = """
SELECT p.name, pit.trip_id
FROM passenger AS p
JOIN pass_in_trip AS pit ON p.id = pit.passenger_id
LIMIT 1"""
with sqlite3.connect('demo.db') as conn:
   df = pd.read_sql_query(query, conn)
print(df)

import sqlite3
import pandas as pd

# 1. SQL-запрос: соединяем пассажиров и их поездки
query = """
SELECT p.name AS passenger_name, pit.trip_id
FROM passenger AS p
JOIN pass_in_trip AS pit ON p.id = pit.passenger_id;
"""

# 2. Подключение к БД и получение данных
with sqlite3.connect('demo.db') as conn:
    df = pd.read_sql_query(query, conn)

# Проверка: если данных нет, не ломаем скрипт, а сообщаем
if df.empty:
    print("⚠️ В базе нет данных о поездках. Проверьте INSERT-запросы в скрипте инициализации.")
else:
    # 3. Агрегация: сколько поездок у каждого пассажира
    stats = (
        df.groupby('passenger_name')['trip_id']
          .count()
          .reset_index()
          .rename(columns={'trip_id': 'trips_count'})
          .sort_values(by='trips_count', ascending=False)
    )

    # Вывод топ-10 в консоль (чтобы сразу видеть результат при запуске)
    print("Топ пассажиров по количеству поездок:")
    print(stats.head(10))

    # 4. Сохранение отчёта в CSV (артефакт для портфолио)
    output_file = 'passenger_trips_report.csv'
    stats.to_csv(output_file, index=False)
    print(f"\n✅ Отчёт успешно сохранён в файл: {output_file}")
