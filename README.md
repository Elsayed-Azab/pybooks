# Pybooks - Library Book Management System

Pybooks is a Library Book Management System designed to streamline the management of library collections and enhance the user experience for both patrons and librarians.

## Purpose and Scope

### Purpose
To create an efficient system that enables libraries to manage book collections and provide users with the ability to search for, borrow, and return books.

### Scope
- **For Patrons:** Users can register, log in, search for books, borrow them, and view their borrowing history.
- **For Librarians:** Librarians can manage the book inventory, including adding, editing, and deleting books, and tracking overdue items.
- **Transaction Logs:** The system tracks all borrowing and returning activities for future reference.

## Features

### Functional Requirements
- User registration, login, and profile management.
- Search functionality for books.
- Borrowing and returning books for patrons.
- Book inventory management for librarians.
- Transaction logging for all borrowing and returning activities.

### Non-Functional Requirements
- **Performance:** Efficiently handles multiple users simultaneously.
- **Usability:** User-friendly interface.
- **Security:** Secure data storage and proper access control.
- **Scalability:** Supports growing user and book inventory.

## Data Requirements
- **Users:** ID, name, email, password, and role.
- **Books:** ID, title, ISBN, publication year, and more.
- **Authors:** ID, name, email.
- **Transactions:** Logs with user ID, book ID, borrow date, return date, and transaction status.

## User Interface
- **Home Page:** Clean interface with a search bar and login/signup links.
- **Login/Register Page:** Forms for account creation and login.
- **Search Results Page:** Displays books matching search queries with availability and author details.
- **Book Details Page:** Detailed book information with borrowing options.
- **User Dashboard:** Displays borrowed books, due dates, and borrowing history.
- **Admin Dashboard:** For managing book inventory and tracking overdue books.

## Technologies Used
- **Backend:** Python with Flask
- **Database:** (Specify if applicable, e.g., SQLite, PostgreSQL, etc.)
- **Frontend:** (Specify if applicable, e.g., HTML/CSS, JavaScript frameworks)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Elsayed-Azab/pybooks.git
