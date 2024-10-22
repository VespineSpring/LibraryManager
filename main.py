import mysql.connector

connection = mysql.connector.connect(host="localhost", user="root", password="root")
cursor = connection.cursor()

cursor.execute("create database if not exists medicalclinic")
cursor.execute("use medicalclinic")

print(connection.database)
