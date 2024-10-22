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
                return_date DATETIME DEFAULT CURRENT_TIMESTAMP
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


def register_user(name, phone):
    cursor.execute("INSERT INTO users (name, phone_number) VALUES (%s, %s)", (name, phone))
    connection.commit()
    print(str(name), " has been successfully added.")


def register_book(title, author):
    cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (title, author))
    connection.commit()
    print(str(title), " by ", str(author), " has been added.")


def register_rental(user_id, book_id):
    cursor.execute("SELECT available FROM books WHERE book_id = %s", (book_id,))
    result = cursor.fetchone()

    if result and result[0] == 1:
        cursor.execute("INSERT INTO rented_books (user_id, book_id) VALUES (%s, %s)", (user_id, book_id))
        cursor.execute("UPDATE books SET available = 0 WHERE book_id = %s", (book_id,))
        connection.commit()
        print("Book rented successfully.")
    else:
        print("Book is not available right now.")
    

def register_return(rental_id):
    cursor.execute("SELECT book_id FROM rented_books WHERE rental_id = %s", (rental_id,))
    result = cursor.fetchone()

    if result:
        book_id = result[0]

        cursor.execute("INSERT INTO returned_books (rental_id) VALUES (%s)", (rental_id,))
        cursor.execute("UPDATE books SET available = 1 WHERE book_id = %s", (book_id,))
        cursor.execute("DELETE FROM rented_books WHERE rental_id = %s", (rental_id,))
        connection.commit()
        print("Book has been returned.")
    else:
        print("Rental ID not found.")


def main():
    while True:
        print("\nLibrary Manager")
        print("1. Add User")
        print("2. Add Book")
        print("3. Rent Book")
        print("4. Return Book")
        print("5. Exit")

        choice = int(input("Enter: "))

        if choice == 1:
            name = input("Enter name: ")
            phone_number = input("Enter phone number: ")
            register_user(name, phone_number)
        elif choice == 2:
            book_title = input("Enter title: ")
            book_author = input("Enter author: ")
            register_book(book_title, book_author)
        elif choice == 3:
            user_id = int(input("Enter user ID: "))
            book_id = int(input("Enter book ID: "))
            register_rental(user_id, book_id)
        elif choice == 4:
            rental_id = int(input("Enter rental ID: "))
            register_return(rental_id)
        elif choice == 5:
            cursor.close()
            connection.close()
            print("Exiting the library manager.")
            break
        else:
            print("Invalid choice. Try again.")
            continue

if __name__ == "__main__":
    main()
