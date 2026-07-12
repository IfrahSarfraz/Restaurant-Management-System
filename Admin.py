import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import oracledb
import hashlib
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AdminPanel:
    def __init__(self, root, connection_params):
        self.root = root
        self.root.title("Admin Panel - Restaurant Management System")
        self.root.geometry("1200x800")
        
        # Store connection parameters
        self.connection_params = connection_params
        self.conn = None
        self.admin_id = None
        
        # Define all tables with their properties (updated based on your screenshots)
        self.tables = {
            "TABLE_INFO_P": {
                "columns": ["TABLEID", "CAPACITY", "BOOKING_STAT", "LOCATION"],
                "update_fields": ["CAPACITY", "BOOKING_STAT", "LOCATION"],
                "pk": "TABLEID"
            },
            "RESERVATION_P": {
                "columns": ["RESERVATIONID", "CUSTOMERID", "TABLEID", "RESERVATIONDATE", "PARTYSIZE", "RESERVATIONSTATUS"],
                "update_fields": ["RESERVATIONSTATUS"],
                "pk": "RESERVATIONID",
                "dropdowns": {
                    "RESERVATIONSTATUS": ["Confirmed", "Pending", "Cancelled", "Completed"]
                }
            },
            "CUSTOMER_P": {
                "columns": ["CUSTOMERID", "NAME", "CONTACT", "EMAIL"],
                "update_fields": ["NAME", "CONTACT", "EMAIL"],
                "pk": "CUSTOMERID",
                "triggers_disabled": True  # Flag to handle trigger issues
            },
            "ORDER_P": {
                "columns": ["ORDERID", "CUSTOMERID", "TABLEID", "TOTALAMOUNT", "ORDERDATE", "PAYMENTSTATUS", "STATUS"],
                "update_fields": ["PAYMENTSTATUS", "STATUS"],
                "pk": "ORDERID",
                "dropdowns": {
                    "STATUS": ["Pending", "Preparing", "Ready", "Delivered", "Cancelled"],
                    "PAYMENTSTATUS": ["Paid", "Unpaid", "Partial"]
                }
            },
            "STAFF_P": {
                "columns": ["STAFFID", "S_NAME", "STAFFROLE", "SHIFTINGTIME", "SALARY"],
                "update_fields": ["S_NAME", "STAFFROLE", "SHIFTINGTIME", "SALARY"],
                "pk": "STAFFID"
            },
            "SUPPLIER_P": {
                "columns": ["SUPPLIERID", "NAME", "CONTACTDETAILS", "COMPANYNAME", "ADDRESS", "EMAIL", "PASSWORD"],
                "update_fields": ["NAME", "CONTACTDETAILS", "COMPANYNAME", "ADDRESS", "EMAIL", "PASSWORD"],
                "pk": "SUPPLIERID"
            },
            "INVENTORY_P": {
                "columns": ["ITEMID", "ITEMNAME", "QUANTITY", "RECORDDATE", "SUPPLIERID"],
                "update_fields": ["ITEMNAME", "QUANTITY", "RECORDDATE", "SUPPLIERID"],
                "pk": "ITEMID"
            }
        }
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.setup_login_tab()
        self.setup_data_view_tab()
        self.setup_report_tab()
    
    def test_connection(self):
        try:
            self.conn = oracledb.connect(
                user=self.connection_params['username'],
                password=self.connection_params['password'],
                dsn=self.connection_params['dsn']
            )
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", f"Connection failed: {str(e)}")
            return False
    
    def setup_login_tab(self):
        self.login_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.login_tab, text='Admin Login')
        
        ttk.Label(self.login_tab, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.login_username = ttk.Entry(self.login_tab)
        self.login_username.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.login_tab, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.login_password = ttk.Entry(self.login_tab, show="*")
        self.login_password.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(self.login_tab, text="Login", command=self.admin_login).grid(row=2, column=0, columnspan=2, pady=10)
        
        self.login_result = ttk.Label(self.login_tab, text="", foreground="red")
        self.login_result.grid(row=3, column=0, columnspan=2)
    
    def admin_login(self):
        if not self.test_connection():
            return
            
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        
        if not username or not password:
            self.login_result.config(text="❌ Username and password are required", foreground="red")
            return
        
        try:
            cursor = self.conn.cursor()
            
            hashed_password = self.hash_password(password)
            
            query = "SELECT adminid FROM admin_P WHERE username = :username AND password = :password"
            cursor.execute(query, {'username': username, 'password': hashed_password})
            result = cursor.fetchone()
            
            if result:
                self.admin_id = result[0]
                self.login_result.config(text="✅ Login successful!", foreground="green")
                
                # Enable other tabs
                self.notebook.tab(self.data_tab, state='normal')
                self.notebook.tab(self.report_tab, state='normal')
                self.notebook.select(self.data_tab)
                
                # Disable login tab
                self.notebook.tab(self.login_tab, state='disabled')
                
                # Load first table by default
                if self.tables:
                    self.table_selector.current(0)
                    self.load_selected_table()
            else:
                self.login_result.config(text="❌ Invalid credentials", foreground="red")
            
            cursor.close()
        except Exception as e:
            self.login_result.config(text=f"❌ Login failed: {str(e)}", foreground="red")
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def setup_data_view_tab(self):
        self.data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.data_tab, text='Manage Data', state='disabled')
        
        # Frame for table selection and controls
        control_frame = ttk.Frame(self.data_tab)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(control_frame, text="Select Table:").pack(side='left', padx=5)
        
        self.table_selector = ttk.Combobox(control_frame, values=list(self.tables.keys()))
        self.table_selector.pack(side='left', padx=5)
        self.table_selector.bind("<<ComboboxSelected>>", self.load_selected_table)
        
        # Action buttons
        self.refresh_btn = ttk.Button(control_frame, text="Refresh", command=self.load_selected_table)
        self.refresh_btn.pack(side='left', padx=5)
        
        self.update_btn = ttk.Button(control_frame, text="Update Selected", command=self.update_selected_record)
        self.update_btn.pack(side='left', padx=5)
        
        self.insert_btn = ttk.Button(control_frame, text="Add New", command=self.add_new_record)
        self.insert_btn.pack(side='left', padx=5)
        
        self.delete_btn = ttk.Button(control_frame, text="Delete Selected", command=self.delete_selected_record)
        self.delete_btn.pack(side='left', padx=5)
        
        # Create a frame for the treeview and scrollbar
        tree_frame = ttk.Frame(self.data_tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create a treeview with scrollbar
        self.data_tree = ttk.Treeview(tree_frame)
        self.data_tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.data_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.data_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.data_tree.bind('<<TreeviewSelect>>', self.on_record_selected)
        
        # Status label
        self.data_status = ttk.Label(self.data_tab, text="Please login as admin to view data", foreground="red")
        self.data_status.pack(pady=5)
    
    def load_selected_table(self, event=None):
        selected_table = self.table_selector.get()
        if not selected_table or not self.conn:
            return
            
        table_info = self.tables.get(selected_table)
        if not table_info:
            return
            
        try:
            cursor = self.conn.cursor()
            
            # Get data from the table
            cursor.execute(f"SELECT * FROM {selected_table}")
            
            # Clear existing columns and data
            self.clear_treeview()
            
            # Set up new columns
            columns = table_info['columns']
            self.data_tree['columns'] = columns
            for col in columns:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=100, anchor='center')
            
            # Add data to treeview
            for row in cursor:
                # Fix None values in ORDERDATE for ORDER_P table
                if selected_table == "ORDER_P" and row[4] is None:
                    row = list(row)
                    row[4] = "Not set"
                    row = tuple(row)
                # Fix display for RESERVATION_P table
                elif selected_table == "RESERVATION_P":
                    row = list(row)
                    if row[5] is None:  # RESERVATIONSTATUS
                        row[5] = "Not set"
                    row = tuple(row)
                self.data_tree.insert("", "end", values=row)
            
            cursor.close()
            self.data_status.config(text=f"Showing data from {selected_table}", foreground="green")
            
        except Exception as e:
            self.data_status.config(text=f"Error loading {selected_table}: {str(e)}", foreground="red")
    
    def on_record_selected(self, event):
        """Handle record selection in treeview"""
        selected_item = self.data_tree.focus()
        if selected_item:
            self.selected_item = selected_item
    
    def clear_treeview(self):
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        self.data_tree['columns'] = []
    
    def update_selected_record(self):
        """Update the selected record"""
        if not hasattr(self, 'selected_item') or not self.selected_item:
            messagebox.showwarning("Warning", "Please select a record to update")
            return
            
        selected_table = self.table_selector.get()
        if not selected_table:
            return
            
        table_info = self.tables.get(selected_table)
        if not table_info:
            return
            
        item_data = self.data_tree.item(self.selected_item)['values']
        if not item_data:
            return
            
        # Get column names
        columns = table_info['columns']
        
        # Create dialog window
        self.update_dialog = tk.Toplevel(self.root)
        self.update_dialog.title(f"Update {selected_table} Record")
        self.update_dialog.geometry("500x400")
        
        # Create scrollable frame
        canvas = tk.Canvas(self.update_dialog)
        scrollbar = ttk.Scrollbar(self.update_dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create form fields for updatable columns
        self.update_entries = {}
        row_idx = 0
        
        for i, col in enumerate(columns):
            if col in table_info['update_fields']:
                ttk.Label(scrollable_frame, text=f"{col}:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="e")
                
                # Handle dropdown fields
                if 'dropdowns' in table_info and col in table_info['dropdowns']:
                    entry = ttk.Combobox(scrollable_frame, values=table_info['dropdowns'][col])
                    entry.set(item_data[i] if item_data[i] else "")
                # Special handling for password field
                elif col.lower() == "password":
                    entry = ttk.Entry(scrollable_frame, show="*")
                else:
                    entry = ttk.Entry(scrollable_frame)
                
                # Handle None values in ORDERDATE
                if selected_table == "ORDER_P" and col == "ORDERDATE" and item_data[i] == "Not set":
                    entry.insert(0, "")
                else:
                    entry.insert(0, item_data[i] if item_data[i] else "")
                
                entry.grid(row=row_idx, column=1, padx=5, pady=5)
                self.update_entries[col] = entry
                row_idx += 1
        
        # Status label
        self.update_status = ttk.Label(scrollable_frame, text="", foreground="red")
        self.update_status.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1
        
        # Save button
        ttk.Button(scrollable_frame, text="Update", 
                 command=lambda: self.save_update(selected_table, table_info, item_data)).grid(row=row_idx, column=0, columnspan=2, pady=10)
    
    def save_update(self, table_name, table_info, original_data):
        """Save the updated record to database"""
        try:
            cursor = self.conn.cursor()
            
            # For CUSTOMER_P table with trigger issues, disable trigger temporarily
            if table_name == "CUSTOMER_P" and table_info.get('triggers_disabled', False):
                cursor.execute("ALTER TRIGGER SYSTEM.UPDATE_CUSTOMER_LOG DISABLE")
            
            # Build the UPDATE statement
            set_clause = []
            params = {}
            pk_column = table_info['pk']
            pk_value = original_data[table_info['columns'].index(pk_column)]
            
            for col, entry in self.update_entries.items():
                value = entry.get() if isinstance(entry, ttk.Combobox) else entry.get().strip()
                
                # Skip empty ORDERDATE (keep as NULL)
                if table_name == "ORDER_P" and col == "ORDERDATE" and not value:
                    continue
                
                # Hash password if this is the password field
                if col.lower() == "password":
                    value = self.hash_password(value)
                
                set_clause.append(f"{col} = :{col}")
                params[col] = value
            
            update_query = f"""
                UPDATE {table_name}
                SET {', '.join(set_clause)}
                WHERE {pk_column} = :pk_value
            """
            params['pk_value'] = pk_value
            
            cursor.execute(update_query, params)
            self.conn.commit()
            
            # Re-enable trigger if we disabled it
            if table_name == "CUSTOMER_P" and table_info.get('triggers_disabled', False):
                cursor.execute("ALTER TRIGGER SYSTEM.UPDATE_CUSTOMER_LOG ENABLE")
            
            cursor.close()
            
            self.update_status.config(text="Record updated successfully!", foreground="green")
            self.load_selected_table()  # Refresh the view
            
            # Close the dialog after 1 second
            self.update_dialog.after(1000, self.update_dialog.destroy)
            
        except Exception as e:
            self.update_status.config(text=f"Error updating record: {str(e)}", foreground="red")
    
    def add_new_record(self):
        """Add a new record"""
        selected_table = self.table_selector.get()
        if not selected_table:
            return
            
        table_info = self.tables.get(selected_table)
        if not table_info:
            return
            
        # Create dialog window
        self.insert_dialog = tk.Toplevel(self.root)
        self.insert_dialog.title(f"Add New {selected_table} Record")
        self.insert_dialog.geometry("500x400")
        
        # Create scrollable frame
        canvas = tk.Canvas(self.insert_dialog)
        scrollbar = ttk.Scrollbar(self.insert_dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create form fields
        self.insert_entries = {}
        row_idx = 0
        
        for col in table_info['columns']:
            # Skip auto-generated ID fields
            if col == table_info['pk'] and col.endswith('ID'):
                continue
                
            ttk.Label(scrollable_frame, text=f"{col}:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="e")
            
            # Handle dropdown fields
            if 'dropdowns' in table_info and col in table_info['dropdowns']:
                entry = ttk.Combobox(scrollable_frame, values=table_info['dropdowns'][col])
            # Special handling for password field (show asterisks)
            elif col.lower() == "password":
                entry = ttk.Entry(scrollable_frame, show="*")
            else:
                entry = ttk.Entry(scrollable_frame)
                
            entry.grid(row=row_idx, column=1, padx=5, pady=5)
            self.insert_entries[col] = entry
            row_idx += 1
        
        # Status label
        self.insert_status = ttk.Label(scrollable_frame, text="", foreground="red")
        self.insert_status.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1
        
        # Save button
        ttk.Button(scrollable_frame, text="Add", 
                 command=lambda: self.save_new(selected_table, table_info)).grid(row=row_idx, column=0, columnspan=2, pady=10)
    
    def save_new(self, table_name, table_info):
        """Save the new record to database"""
        try:
            cursor = self.conn.cursor()
            
            # For CUSTOMER_P table with trigger issues, disable trigger temporarily
            if table_name == "CUSTOMER_P" and table_info.get('triggers_disabled', False):
                cursor.execute("ALTER TRIGGER SYSTEM.INS_CUSTOMER_LOG DISABLE")
            
            # Build the INSERT statement
            columns = []
            values = []
            params = {}
            
            for col, entry in self.insert_entries.items():
                value = entry.get() if isinstance(entry, ttk.Combobox) else entry.get().strip()
                
                # Handle empty values for required fields
                if not value and col in ['PASSWORD', 'EMAIL']:
                    messagebox.showerror("Error", f"{col} is a required field")
                    return
                
                # Hash password if this is the password field
                if col.lower() == "password":
                    value = self.hash_password(value)
                
                columns.append(col)
                values.append(f":{col}")
                params[col] = value
            
            insert_query = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({', '.join(values)})
            """
            
            cursor.execute(insert_query, params)
            self.conn.commit()
            
            # Re-enable trigger if we disabled it
            if table_name == "CUSTOMER_P" and table_info.get('triggers_disabled', False):
                cursor.execute("ALTER TRIGGER SYSTEM.INS_CUSTOMER_LOG ENABLE")
            
            cursor.close()
            
            self.insert_status.config(text="Record added successfully!", foreground="green")
            self.load_selected_table()  # Refresh the view
            
            # Close the dialog after 1 second
            self.insert_dialog.after(1000, self.insert_dialog.destroy)
            
        except Exception as e:
            self.insert_status.config(text=f"Error adding record: {str(e)}", foreground="red")
    
    def delete_selected_record(self):
        """Delete the selected record"""
        if not hasattr(self, 'selected_item') or not self.selected_item:
            messagebox.showwarning("Warning", "Please select a record to delete")
            return
            
        selected_table = self.table_selector.get()
        if not selected_table:
            return
            
        table_info = self.tables.get(selected_table)
        if not table_info:
            return
            
        item_data = self.data_tree.item(self.selected_item)['values']
        if not item_data:
            return
            
        # Get column names
        columns = table_info['columns']
        
        # Confirm deletion
        confirm_msg = f"Are you sure you want to delete this {selected_table} record?\n\n"
        for i, col in enumerate(columns[:5]):  # Show first 5 columns for confirmation
            confirm_msg += f"{col}: {item_data[i]}\n"
        
        if not messagebox.askyesno("Confirm Delete", confirm_msg):
            return
            
        try:
            cursor = self.conn.cursor()
            
            # For CUSTOMER_P table with trigger issues, disable trigger temporarily
            if selected_table == "CUSTOMER_P" and table_info.get('triggers_disabled', False):
                cursor.execute("ALTER TRIGGER SYSTEM.DEL_CUSTOMER_LOG DISABLE")
            
            # Build the DELETE statement
            pk_column = table_info['pk']
            pk_value = item_data[columns.index(pk_column)]
            
            delete_query = f"""
                DELETE FROM {selected_table}
                WHERE {pk_column} = :pk_value
            """
            
            cursor.execute(delete_query, {'pk_value': pk_value})
            self.conn.commit()
            
            # Re-enable trigger if we disabled it
            if selected_table == "CUSTOMER_P" and table_info.get('triggers_disabled', False):
                cursor.execute("ALTER TRIGGER SYSTEM.DEL_CUSTOMER_LOG ENABLE")
            
            cursor.close()
            
            self.data_status.config(text="Record deleted successfully", foreground="green")
            self.load_selected_table()  # Refresh the view
            
        except Exception as e:
            self.data_status.config(text=f"Error deleting record: {str(e)}", foreground="red")
    
    def setup_report_tab(self):
        """Setup the report generation tab"""
        self.report_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.report_tab, text='Generate Reports', state='disabled')
        
        # Report selection frame
        report_select_frame = ttk.LabelFrame(self.report_tab, text="Select Report Type")
        report_select_frame.pack(fill='x', padx=10, pady=10)
        
        # Report types
        self.report_types = ttk.Combobox(report_select_frame, values=[
            "Sales Report",
            "Inventory Status",
            "Customer Orders",
            "Staff Performance",
            "Supplier Analysis"
        ])
        self.report_types.pack(pady=5)
        self.report_types.current(0)
        
        # Date range selection
        date_frame = ttk.Frame(report_select_frame)
        date_frame.pack(fill='x', pady=5)
        
        ttk.Label(date_frame, text="From:").pack(side='left')
        self.start_date = ttk.Entry(date_frame)
        self.start_date.pack(side='left', padx=5)
        self.start_date.insert(0, datetime.now().strftime('%Y-%m-01'))
        
        ttk.Label(date_frame, text="To:").pack(side='left', padx=(10,0))
        self.end_date = ttk.Entry(date_frame)
        self.end_date.pack(side='left', padx=5)
        self.end_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Generate button
        ttk.Button(report_select_frame, text="Generate Report", command=self.generate_report).pack(pady=10)
        
        # Report display area
        report_display_frame = ttk.Frame(self.report_tab)
        report_display_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Text widget for report display
        self.report_text = tk.Text(report_display_frame, wrap='word')
        self.report_text.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(report_display_frame, command=self.report_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.report_text.config(yscrollcommand=scrollbar.set)
        
        # Export buttons
        button_frame = ttk.Frame(self.report_tab)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Export to CSV", command=self.export_to_csv).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Export to Excel", command=self.export_to_excel).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Show Chart", command=self.show_chart).pack(side='left', padx=5)
        
        # Status label
        self.report_status = ttk.Label(self.report_tab, text="", foreground="red")
        self.report_status.pack(pady=5)
        
        # Store report data
        self.report_data = None
    
    def generate_report(self):
        """Generate the selected report"""
        report_type = self.report_types.get()
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        
        if not report_type:
            self.report_status.config(text="Please select a report type", foreground="red")
            return
            
        try:
            cursor = self.conn.cursor()
            
            if report_type == "Sales Report":
                query = """
                SELECT TO_CHAR(o.orderdate, 'YYYY-MM-DD') AS order_date, 
                       COUNT(*) AS total_orders,
                       SUM(o.totalamount) AS total_sales
                FROM order_p o
                WHERE o.orderdate BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') 
                                      AND TO_DATE(:end_date, 'YYYY-MM-DD')
                GROUP BY TO_CHAR(o.orderdate, 'YYYY-MM-DD')
                ORDER BY order_date
                """
                cursor.execute(query, {'start_date': start_date, 'end_date': end_date})
                
            elif report_type == "Inventory Status":
                query = """
                SELECT i.itemname, i.quantity, s.name AS supplier, 
                       CASE WHEN i.quantity < 10 THEN 'Low' 
                            WHEN i.quantity < 30 THEN 'Medium' 
                            ELSE 'High' END AS stock_level
                FROM inventory_p i
                JOIN supplier_p s ON i.supplierid = s.supplierid
                ORDER BY stock_level, i.itemname
                """
                cursor.execute(query)
                
            elif report_type == "Customer Orders":
                query = """
                SELECT c.name, COUNT(o.orderid) AS order_count, 
                       SUM(o.totalamount) AS total_spent
                FROM customer_p c
                JOIN order_p o ON c.customerid = o.customerid
                WHERE o.orderdate BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') 
                                      AND TO_DATE(:end_date, 'YYYY-MM-DD')
                GROUP BY c.name
                ORDER BY total_spent DESC
                """
                cursor.execute(query, {'start_date': start_date, 'end_date': end_date})
                
            elif report_type == "Staff Performance":
                query = """
                SELECT s.s_name, s.staffrole, COUNT(o.orderid) AS orders_handled
                FROM staff_p s
                JOIN order_p o ON s.staffid = o.staffid
                WHERE o.orderdate BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') 
                                      AND TO_DATE(:end_date, 'YYYY-MM-DD')
                GROUP BY s.s_name, s.staffrole
                ORDER BY orders_handled DESC
                """
                cursor.execute(query, {'start_date': start_date, 'end_date': end_date})
                
            elif report_type == "Supplier Analysis":
                query = """
                SELECT s.name, s.companyname, COUNT(i.itemid) AS items_supplied,
                       SUM(i.quantity) AS total_quantity
                FROM supplier_p s
                JOIN inventory_p i ON s.supplierid = i.supplierid
                GROUP BY s.name, s.companyname
                ORDER BY items_supplied DESC
                """
                cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            # Store the data for export
            self.report_data = (columns, rows)
            
            # Format the report for display
            self.report_text.delete(1.0, tk.END)
            
            # Add report header
            self.report_text.insert(tk.END, f"{report_type}\n", 'header')
            self.report_text.insert(tk.END, f"Date Range: {start_date} to {end_date}\n\n", 'subheader')
            
            # Add column headers
            col_width = max(len(col) for col in columns) + 2
            header = "".join(f"{col:<{col_width}}" for col in columns)
            self.report_text.insert(tk.END, header + "\n", 'bold')
            self.report_text.insert(tk.END, "-" * len(header) + "\n")
            
            # Add data rows
            for row in rows:
                row_str = "".join(f"{str(value):<{col_width}}" for value in row)
                self.report_text.insert(tk.END, row_str + "\n")
            
            cursor.close()
            self.report_status.config(text=f"Report generated successfully", foreground="green")
            
            # Configure text tags for formatting
            self.report_text.tag_configure('header', font=('Arial', 14, 'bold'), justify='center')
            self.report_text.tag_configure('subheader', font=('Arial', 10), justify='center')
            self.report_text.tag_configure('bold', font=('Arial', 10, 'bold'))
            
        except Exception as e:
            self.report_status.config(text=f"Error generating report: {str(e)}", foreground="red")
    
    def export_to_csv(self):
        """Export the current report data to CSV"""
        if not self.report_data:
            messagebox.showwarning("Warning", "No report data to export")
            return
            
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if file_path:
                columns, rows = self.report_data
                df = pd.DataFrame(rows, columns=columns)
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", "Report exported to CSV successfully")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def export_to_excel(self):
        """Export the current report data to Excel"""
        if not self.report_data:
            messagebox.showwarning("Warning", "No report data to export")
            return
            
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if file_path:
                columns, rows = self.report_data
                df = pd.DataFrame(rows, columns=columns)
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", "Report exported to Excel successfully")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel: {str(e)}")
    
    def show_chart(self):
        """Display a chart of the current report data"""
        if not self.report_data:
            messagebox.showwarning("Warning", "No report data to visualize")
            return
            
        try:
            columns, rows = self.report_data
            df = pd.DataFrame(rows, columns=columns)
            
            # Create a new window for the chart
            chart_window = tk.Toplevel(self.root)
            chart_window.title("Report Visualization")
            
            # Determine chart type based on report type
            report_type = self.report_types.get()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if report_type == "Sales Report" and len(df) > 0:
                df['order_date'] = pd.to_datetime(df.iloc[:, 0])
                df = df.sort_values('order_date')
                ax.plot(df['order_date'], df.iloc[:, 2], marker='o')
                ax.set_title("Daily Sales Report")
                ax.set_xlabel("Date")
                ax.set_ylabel("Total Sales")
                plt.xticks(rotation=45)
                
            elif report_type == "Inventory Status" and len(df) > 0:
                stock_levels = df.iloc[:, 3].value_counts()
                stock_levels.plot(kind='pie', autopct='%1.1f%%', ax=ax)
                ax.set_title("Inventory Stock Levels")
                ax.set_ylabel("")
                
            elif report_type == "Customer Orders" and len(df) > 0:
                df = df.head(10)  # Show top 10 customers
                ax.bar(df.iloc[:, 0], df.iloc[:, 2])
                ax.set_title("Top Customers by Spending")
                ax.set_xlabel("Customer")
                ax.set_ylabel("Total Spent")
                plt.xticks(rotation=45)
                
            elif report_type == "Staff Performance" and len(df) > 0:
                ax.bar(df.iloc[:, 0], df.iloc[:, 2])
                ax.set_title("Staff Performance by Orders Handled")
                ax.set_xlabel("Staff Member")
                ax.set_ylabel("Number of Orders")
                plt.xticks(rotation=45)
                
            elif report_type == "Supplier Analysis" and len(df) > 0:
                ax.bar(df.iloc[:, 1], df.iloc[:, 2])
                ax.set_title("Items Supplied by Company")
                ax.set_xlabel("Company")
                ax.set_ylabel("Number of Items")
                plt.xticks(rotation=45)
                
            else:
                messagebox.showinfo("Info", "No suitable data for visualization")
                chart_window.destroy()
                return
            
            # Embed the chart in the Tkinter window
            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create chart: {str(e)}")

def open_admin_panel(connection_params):
    admin_root = tk.Toplevel()
    admin_root.title("Admin Panel")
    AdminPanel(admin_root, connection_params)
    admin_root.mainloop()

if __name__ == "__main__":
    # For testing the admin panel standalone
    root = tk.Tk()
    connection_params = {
        'username': 'system',
        'password': 'Layby9898',
        'dsn': 'localhost:1521/orcl1'
    }
    AdminPanel(root, connection_params)
    root.mainloop()