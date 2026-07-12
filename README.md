# Restaurant Management System

A desktop-based Restaurant Management System built with **Python (Tkinter)** for the GUI and **Oracle Database** for data storage. The system supports four user roles — **Customer, Admin, Staff, and Supplier** — each with a dedicated login and panel, and covers core restaurant operations such as table reservations, ordering, billing, inventory, staff management, and financial reporting.

## Features

- **Customer Panel** — customer registration/login, browsing the menu, placing orders, reserving tables, viewing order history, and submitting feedback.
- **Admin Panel** — manages staff, inventory, dishes/menu items, billing, tables, reservations, and views financial reports (with data visualizations via `matplotlib`/`pandas`).
- **Staff Panel** — role-based views for Waiter, Kitchen, and Management staff (e.g. table assignments, order preparation status).
- **Supplier Panel** — supplier login and inventory replenishment workflow.
- **Reservations & Billing** — table booking, order-to-bill generation, tax handling, and payment tracking.
- **Reporting** — financial report generation and review for admin/accounting teams.

## Entity-Relationship Diagram (EERD)

The diagram below models the core entities of the system — Customers, Orders, Reservations, Billing, Staff (Waiter/Kitchen/Management), Inventory, Suppliers, Feedback, Financial Reports, and the Accounting Team/Sales Tax relationship.

![Restaurant Management System - Enhanced ER Diagram]<img width="1851" height="1061" alt="Image" src="https://github.com/user-attachments/assets/3602db43-5e97-4ed4-a577-76a854c181f2" />

## Tech Stack

| Layer            | Technology                          |
|-------------------|--------------------------------------|
| GUI               | Python `tkinter`, `ttk`             |
| Database          | Oracle Database (via `oracledb`)     |
| Data & Reporting  | `pandas`, `matplotlib`               |
| Database Logic    | PL/SQL stored procedures, views, and triggers |

## Project Structure

```
Restaurant-Management-System/
├── main.py                              # Application entry point (role selection: Customer/Admin/Staff/Supplier)
├── AdminAuth.py                         # Admin authentication
├── Admin.py                             # Admin dashboard and management panel
├── Customer.py                          # Customer-side interface and operations
├── Staff.py                             # Staff panel (Waiter/Kitchen/Management)
├── Supplier.py                          # Supplier login and inventory replenishment
├── Table Queries.txt                    # SQL DDL — table creation scripts for all entities
├── Procedure, views and tiggers.txt     # PL/SQL stored procedures, views, and triggers
└── docs/
    └── EERD.png                         # Enhanced Entity-Relationship Diagram
```

## Database Setup

1. Install **Oracle Database** (or use an existing instance) along with the `oracledb` Python driver:
   ```bash
   pip install oracledb pandas matplotlib
   ```
2. Run the DDL statements in `Table Queries.txt` to create all tables (Customer, Order, Reservation, Table, Bill, Staff, Inventory, Supplier, Feedback, FinancialReport, etc.).
3. Run the PL/SQL objects in `Procedure, views and tiggers.txt` to create the stored procedures, views, and triggers used by the application (e.g. `reserve_table`, `take_feedback`).
4. Update the database connection parameters (username, password, DSN) in `main.py` to match your Oracle instance.

## Running the Application

```bash
python main.py
```

From the landing screen, choose a role — **Customer, Admin, Staff, or Supplier** — to log in and access the corresponding panel.

## Author

Developed as part of a Software Engineering coursework project.

## License

This project is available for educational and academic use.
