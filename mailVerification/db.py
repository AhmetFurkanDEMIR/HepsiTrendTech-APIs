import psycopg2

conn = psycopg2.connect(
    host="",
    database="",
    port="",
    user="",
    password="")


cursor = conn.cursor()