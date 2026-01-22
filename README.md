# 💰  Household Management System

A robust, Python-based desktop application designed to streamline financial tracking for personal, family, and business needs. This application features a modern GUI, secure authentication, and powerful analytics to visualize spending habits.

## 📖 Overview

The **Household Management System** (also known as Smart Expense Manager) is a standalone application built with Python and Tkinter. It replaces manual spreadsheets with an intuitive interface that allows users to log expenses, categorize transactions, and view real-time insights through interactive charts. It supports multiple distinct sections (Personal, Family, Business) to keep different financial aspects organized but accessible under one account.

## ✨ Key Features

*   **🔐 Secure Authentication**
    *   User registration and login system.
    *   SHA-256 password hashing for security.
    *   Session management.

*   **📂 Multi-Section Tracking**
    *   Dedicated workspaces for **Personal**, **Family**, and **Business** expenses.
    *   Color-coded themes for each section.

*   **📊 Advanced Analytics Dashboard**
    *   **Pie Charts**: Visual breakdown of spending by category.
    *   **Bar Charts**: Comparative view of expenses.
    *   **Trend Analysis**: Line graphs showing daily spending trends.
    *   **Category Stats**: Detailed tabular breakdown with percentages.

*   **📝 Expense Management (CRUD)**
    *   Add, Edit, and Delete expense records.
    *   Customizable categories.
    *   Filter by Year and Month.

*   **📥 Data Import & Export**
    *   **Bulk Import**: Upload CSV files to add multiple expenses at once with validation.
    *   **Export**: Download monthly reports as CSV files.

*   **🎨 Modern UI/UX**
    *   Dark/Light mode elements with a professional color palette.
    *   Responsive layout with Tkinter `ttk` styling.
    *   Fullscreen analytics windows.

## 🛠️ Tech Stack

*   **Language**: Python 3.x
*   **GUI Framework**: Tkinter (Standard Python GUI)
*   **Data Manipulation**: Pandas, CSV module
*   **Visualization**: Matplotlib
*   **Security**: Hashlib (SHA-256)

## 🚀 Installation

Follow these steps to get a local copy up and running.

### Prerequisites

*   Python 3.7 or higher installed on your system.

### Steps

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/expense-manager.git
    ```

2.  **Navigate to the Directory**
    ```bash
    cd expense-manager
    ```

3.  **Install Dependencies**
    This project requires `pandas` and `matplotlib`.
    ```bash
    pip install pandas matplotlib
    ```
    *(Note: Tkinter usually comes pre-installed with Python. If not, you may need to install `python-tk` via your OS package manager).*

4.  **Run the Application**
    ```bash
    python Project.py
    ```

    **⚖️ License
This project is licensed under the MIT License.
Free to use, modify, and distribute with attribution.

👨‍💻 Author
Atharva Pisal**

