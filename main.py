import mysql.connector as sqltor
from tabulate import tabulate
from datetime import datetime


def create_database_and_table():
    connection = sqltor.connect(
        host="localhost", user="root", password="root", charset="utf8"
    )

    if connection.is_connected():
        cursor = connection.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS librarymanager")
        cursor.execute("USE librarymanager")

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS members (
                member_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(10) NOT NULL,
                email VARCHAR(100) NOT NULL,
                joining_data DATETIME DEFAULT CURRENT_TIMESTAMP
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
                member_id INT,
                book_id INT,
                rental_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                returned INT DEFAULT 0
            )
            """
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS returned_books (
                return_id INT AUTO_INCREMENT PRIMARY KEY,
                rental_id INT,
                return_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                fine DECIMAL(10, 2)
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
    host="localhost",
    user="root",
    password="root",
    database="librarymanager",
    charset="utf8",
)
cursor = connection.cursor()


def register_member(name, phone, email):
    cursor.execute(
        "SELECT * FROM members WHERE phone = %s OR email = %s", (phone, email)
    )
    result = cursor.fetchone()

    if result:
        print("Account with this phone number or email already exists.")
    else:
        cursor.execute(
            "INSERT INTO members (name, phone, email) VALUES (%s, %s, %s)",
            (name, phone, email),
        )
        connection.commit()
        print("{} has been successfully added.".format(name))


def register_book(title, author):
    cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (title, author))
    connection.commit()
    print("{} by {} has been added.".format(title, author))


def register_rental(member_id, book_id):
    cursor.execute("SELECT available FROM books WHERE book_id = %s", (book_id,))
    result = cursor.fetchone()

    if result and result[0] == 1:
        cursor.execute(
            "INSERT INTO rented_books (member_id, book_id) VALUES (%s, %s)",
            (member_id, book_id),
        )
        cursor.execute("UPDATE books SET available = 0 WHERE book_id = %s", (book_id,))
        connection.commit()
        print(
            "Book {} has been rented to member {} successfully.".format(
                book_id, member_id
            )
        )
    else:
        print("Book is not available right now.")


def calculate_fine(rental_date, return_date):
    days = (return_date - rental_date).days

    if days <= 7:
        return 0.0

    fine = 0.0
    overdue_days = days - 7
    current_week = 1

    while overdue_days > 0:
        if current_week == 1:
            fine += min(overdue_days, 7) * 0.2
        else:
            fine += min(overdue_days, 7) * (0.2 * (current_week + 1))

        overdue_days -= 7
        current_week += 1

    return fine


def register_return(rental_id):
    cursor.execute(
        "SELECT book_id, rental_date, returned FROM rented_books WHERE rental_id = %s",
        (rental_id,),
    )
    result = cursor.fetchone()

    if result:
        book_id = result[0]
        rental_date = result[1]
        returned = result[2]

        if returned == 1:
            print("This book has already been returned.")
            return

        return_date = datetime.now()
        fine = calculate_fine(rental_date, return_date)

        cursor.execute(
            "INSERT INTO returned_books (rental_id, fine) VALUES (%s, %s)",
            (rental_id, fine),
        )
        cursor.execute("UPDATE books SET available = 1 WHERE book_id = %s", (book_id,))
        cursor.execute(
            "UPDATE rented_books SET returned = 1 WHERE rental_id = %s", (rental_id,)
        )
        connection.commit()
        print(
            "Book {} has been returned successfully with a fine of {}.".format(
                book_id, fine
            )
        )
    else:
        print("Rental ID not found.")


def remove_member(member_id):
    cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
    result = cursor.fetchone()

    if result:
        confirmation = input(
            "Are you sure you want to remove Member ID {}? Type 'yes' to confirm: ".format(
                member_id
            )
        )
        if confirmation.lower() == "yes":
            cursor.execute("DELETE FROM members WHERE member_id = %s", (member_id,))
            connection.commit()
            print("Member ID {} has been removed.".format(member_id))
        else:
            print("Member ID {} removal has been canceled.".format(member_id))
    else:
        print("Member ID not found.")


def remove_book(book_id):
    cursor.execute("SELECT available FROM books WHERE book_id = %s", (book_id,))
    result = cursor.fetchone()

    if result:
        available = result[0]

        if available == 0:
            print(
                "Book ID {} cannot be removed because it is currently rented out.".format(
                    book_id
                )
            )
            return

        confirmation = input(
            "Are you sure you want to remove Book ID {}? Type 'yes' to confirm: ".format(
                book_id
            )
        )
        if confirmation.lower() == "yes":
            cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            connection.commit()
            print("Book ID {} has been removed.".format(book_id))
        else:
            print("Book ID {} removal has been canceled.".format(book_id))
    else:
        print("Book ID not found.")


def show_members():
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()

    print("\nMembers of Library:")

    if members:
        headers = ["ID", "Name", "Phone Number", "Email", "Joining Date"]
        print(tabulate(members, headers=headers, tablefmt="pretty"))
    else:
        print("There are no members in the library.")


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
        data = []

        for book in rented_books:
            if book[4] == 1:
                returned = "Yes"
            else:
                returned = "No"

            data.append([book[0], book[1], book[2], book[3], returned])

        headers = ["ID", "User ID", "Book ID", "Rental Date", "Returned"]
        print(tabulate(data, headers=headers, tablefmt="pretty"))
    else:
        print("No books has been rented.")


def show_returned_books():
    cursor.execute("SELECT * FROM returned_books")
    returned_books = cursor.fetchall()

    print("\nReturned Books:")

    if returned_books:
        headers = ["ID", "Rental ID", "Return Date", "Fine ($)"]
        print(tabulate(returned_books, headers=headers, tablefmt="pretty"))
    else:
        print("No books has been returned.")


def show_commands_menu():
    print("\nCommand Menu")
    menu_options = [
        [1, "Add Member", "Register a new member with name and phone number."],
        [2, "Add Book", "Register a new book with title and author."],
        [3, "Rent Book", "Rent a book by entering user ID and book ID."],
        [4, "Return Book", "Return a rented book using the rental ID."],
        [5, "Show members", "Display all registered members."],
        [6, "Show Books", "Display all registered books."],
        [7, "Show Rented Books", "Display all currently rented books."],
        [8, "Show Returned Books", "Display all returned books."],
        [9, "Remove Member", "Remove a member from the library."],
        [10, "Remove Book", "Remove a book from the library."],
        [11, "Drop DB!!!", "Danger! Drop the entire library database [TEMP]."],
        [12, "Drop Table!", "Danger! Drop the entire table [TEMP]."],
        [13, "Exit", "Exit the library manager."],
    ]

    headers = ["Option", "Command", "Description"]
    print(tabulate(menu_options, headers=headers, tablefmt="pretty"))


def main_menu():
    heading = ["Library Manager"]
    menu_data = [
        [
            "Welcome to Library Manager App! This is a CS project by the students of Class 12.\nStudents: Anam, Ritika and Atharv"
        ],
        ["NOTE: Type `0` to get help for commands."],
    ]

    return tabulate(menu_data, headers=heading, tablefmt="pretty")


print(main_menu())


while True:
    choice = int(input("\nEnter Command: "))

    if choice == 0:
        show_commands_menu()
    elif choice == 1:
        name = input("Enter Name: ")

        while True:
            phone = input("Enter Phone: ")

            if len(phone) != 10:
                print("Phone number should be of 10 digits.")
                continue

            break

        email = input("Enter Email: ")
        register_member(name, phone, email)
    elif choice == 2:
        book_title = input("Enter Title: ")
        book_author = input("Enter Author: ")
        register_book(book_title, book_author)
    elif choice == 3:
        member_id = int(input("Enter User ID: "))
        book_id = int(input("Enter Book ID: "))
        register_rental(member_id, book_id)
    elif choice == 4:
        rental_id = int(input("Enter Rental ID: "))
        register_return(rental_id)
    elif choice == 5:
        show_members()
    elif choice == 6:
        show_books()
    elif choice == 7:
        show_rented_books()
    elif choice == 8:
        show_returned_books()
    elif choice == 9:
        member_id = int(input("Enter Member ID to remove: "))
        remove_member(member_id)
    elif choice == 10:
        book_id = int(input("Enter Book ID to remove: "))
        remove_book(book_id)
    elif choice == 11:
        cursor.execute("DROP DATABASE librarymanager")
        print("Database dropped.")
        cursor.close()
        connection.close()
        print("Exiting the library manager.")
        break
    elif choice == 12:
        while True:
            table = input("Table Name: ")

            cursor.execute("SHOW TABLES LIKE %s", (table,))
            result = cursor.fetchone()

            if result:
                cursor.execute("DROP TABLE {}".format(table))
                connection.commit()
                print("Table Dropped.")
                break
            else:
                print("Wrong name.")
    elif choice == 13:
        cursor.close()
        connection.close()
        print("Exiting the library manager.")
        break
    else:
        print("Invalid choice. Try again.")
