import mysql.connector as sqltor
from tabulate import tabulate


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
    cursor.execute(
        "INSERT INTO users (name, phone_number) VALUES (%s, %s)", (name, phone)
    )
    connection.commit()
    print("{} has been successfully added.".format(name))


def register_book(title, author):
    cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (title, author))
    connection.commit()
    print(str(title), "by", str(author), "has been added.")


def register_rental(user_id, book_id):
    cursor.execute("SELECT available FROM books WHERE book_id = %s", (book_id,))
    result = cursor.fetchone()

    if result and result[0] == 1:
        cursor.execute(
            "INSERT INTO rented_books (user_id, book_id) VALUES (%s, %s)",
            (user_id, book_id),
        )
        cursor.execute("UPDATE books SET available = 0 WHERE book_id = %s", (book_id,))
        connection.commit()
        print(f"Book rented successfully.")
    else:
        print("Book is not available right now.")


def register_return(rental_id):
    cursor.execute(
        "SELECT book_id FROM rented_books WHERE rental_id = %s", (rental_id,)
    )
    result = cursor.fetchone()

    if result:
        book_id = result[0]

        cursor.execute(
            "INSERT INTO returned_books (rental_id) VALUES (%s)", (rental_id,)
        )
        cursor.execute("UPDATE books SET available = 1 WHERE book_id = %s", (book_id,))
        cursor.execute("DELETE FROM rented_books WHERE rental_id = %s", (rental_id,))
        connection.commit()
        print("Book has been returned.")
    else:
        print("Rental ID not found.")


def show_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    print("\nMembers of Library:")

    if users:
        headers = ["ID", "Name", "Phone Number"]
        print(tabulate(users, headers=headers, tablefmt="pretty"))
    else:
        print("There are no memebers in the library.")


def show_books():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    print("\nBooks of Library:")

    if books:
        data = []

        for book in books:
            if book[3] == 1:
                available = "Yes"
            else:
                available = "No"

            data.append([book[0], book[1], book[2], available])

        headers = ["ID", "Title", "Author", "Available"]
        print(tabulate(data, headers=headers, tablefmt="pretty"))
    else:
        print("There are no books in the library.")


def show_rented_books():
    cursor.execute("SELECT * FROM rented_books")
    rented_books = cursor.fetchall()

    print("\nRented Books:")

    if rented_books:
        headers = ["ID", "User ID", "Book ID", "Rental Date"]
        print(tabulate(rented_books, headers=headers, tablefmt="pretty"))
    else:
        print("No books has been rented.")


def show_returned_books():
    cursor.execute("SELECT * FROM returned_books")
    returned_books = cursor.fetchall()

    print("\nReturned Books:")

    if returned_books:
        headers = ["ID", "Rental ID", "Return Date"]
        print(tabulate(returned_books, headers=headers, tablefmt="pretty"))
    else:
        print("No books has been returned.")


def show_menu():
    menu_options = [
        [1, "Add Member", "Register a new member with name and phone number"],
        [2, "Add Book", "Register a new book with title and author"],
        [3, "Rent Book", "Rent a book by entering user ID and book ID"],
        [4, "Return Book", "Return a rented book using the rental ID"],
        [5, "Show members", "Display all registered members"],
        [6, "Show Books", "Display all registered books"],
        [7, "Show Rented Books", "Display all currently rented books"],
        [8, "Show Returned Books", "Display all returned books"],
        [9, "Drop DB!!!", "Danger! Drop the entire library database"],
        [10, "Exit", "Exit the library manager"],
    ]

    headers = ["Option", "Command", "Description"]
    print(tabulate(menu_options, headers=headers, tablefmt="pretty"))


while True:
    print("\nLibrary Manager")
    show_menu()

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
        show_users()
    elif choice == 6:
        show_books()
    elif choice == 7:
        show_rented_books()
    elif choice == 8:
        show_returned_books()
    elif choice == 9:
        cursor.execute("DROP DATABASE librarymanager")
        print("Database dropped.")
        cursor.close()
        connection.close()
        print("Exiting the library manager.")
        break
    elif choice == 10:
        cursor.close()
        connection.close()
        print("Exiting the library manager.")
        break
    else:
        print("Invalid choice. Try again.")
