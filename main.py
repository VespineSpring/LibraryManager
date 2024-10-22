import mysql.connector as sqltor


def create_database_and_table():
    connection = sqltor.connect(host="localhost", user="root", password="root")

    if connection.is_connected():
        cursor = connection.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS librarymanager")
        cursor.execute("USE librarymanager")

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone_number VARCHAR(10) NOT NULL
            )
            """
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS books (
                book_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                author VARCHAR(100) NOT NULL,
                available INT DEFAULT 1
            )
            """
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS rented_books (
                rental_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                book_id INT,
                rental_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (book_id) REFERENCES books(book_id)
            )
            """
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS returned_books (
                return_id INT AUTO_INCREMENT PRIMARY KEY,
                rental_id INT,
                return_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rental_id) REFERENCES rented_books(rental_id)
            )
            """
        )
    else:
        print("Error while connecting the database.")
        return

    cursor.close()
    connection.close()


create_database_and_table()

connection = sqltor.connect(
    host="localhost", user="root", password="root", database="librarymanager"
)
cursor = connection.cursor()

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

for table in tables:
    print(table[0])

cursor.close()
connection.close()
