import tkinter as tk
from tkinter import ttk, messagebox
import oracledb
import hashlib
from datetime import datetime
from PIL import Image, ImageTk

class DatabaseTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System - Customer")
        self.root.geometry("1200x800")
        
        # Set default connection parameters
        self.conn_username = tk.StringVar(value="system")
        self.conn_password = tk.StringVar(value="Layby9898")
        self.conn_dsn = tk.StringVar(value="localhost:1521/orcl1")
        
        # Load background image
        try:
            self.bg_image = Image.open("restaurant_bg.jpg")  # Replace with your image path
            self.bg_image = self.bg_image.resize((1200, 800), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        except:
            self.bg_photo = None
        
        # Create main container
        self.main_container = tk.Frame(root)
        self.main_container.pack(fill='both', expand=True)
        
        # Create left panel for buttons
        self.left_panel = tk.Frame(self.main_container, width=200, bg="#f1d8b3")
        self.left_panel.pack(side='left', fill='y')
        self.left_panel.pack_propagate(False)
        
        # Create right panel for content
        self.right_panel = tk.Frame(self.main_container)
        self.right_panel.pack(side='right', fill='both', expand=True)
        
        # Add background to right panel
        if self.bg_photo:
            self.bg_label = tk.Label(self.right_panel, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            welcome_label = tk.Label(self.right_panel, 
                                    text="Welcome to Gourmet Delights Restaurant", 
                                    font=('Helvetica', 24, 'bold'),
                                    bg='#cdffd8', fg='#f1d8b3')
            welcome_label.place(relx=0.5, rely=0.5, anchor='center')
        else:
            self.right_panel.config(bg='#cdffd8')
            welcome_label = tk.Label(self.right_panel, 
                                    text="Welcome to Gourmet Delights Restaurant", 
                                    font=('Helvetica', 24, 'bold'),
                                    bg='#cdffd8', fg='#2c3e50')
            welcome_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Add buttons to left panel
        self.create_left_panel_buttons()
        
        # Initialize variables for tabs
        self.order_tab = None
        self.reservation_tab = None
        self.feedback_tab = None
        self.view_menu_tab = None
        
        self.last_order_id = None
        
        # Test connection silently on startup
        self.test_connection(silent=True)

    def create_left_panel_buttons(self):
        # Title label
        title_label = tk.Label(self.left_panel, text="Customer Panel", 
                             font=('Helvetica', 14, 'bold'), 
                             bg="#a0754b", fg="white", pady=10)
        title_label.pack(fill='x')
        
        # Buttons
        button_style = {'font': ('Helvetica', 12), 'bg': '#a0754b', 'fg': 'white', 
                       'activebackground': '#a0754b', 'activeforeground': 'white',
                       'relief': 'flat', 'bd': 0, 'padx': 10, 'pady': 10}
        
        place_order_btn = tk.Button(self.left_panel, text="Place Order", 
                                  command=self.show_order_tab, **button_style)
        place_order_btn.pack(fill='x', pady=(20, 5))
        
        reservation_btn = tk.Button(self.left_panel, text="Table Reservation", 
                                  command=self.show_reservation_tab, **button_style)
        reservation_btn.pack(fill='x', pady=5)
        
        view_menu_btn = tk.Button(self.left_panel, text="View Menu", 
                                command=self.show_view_menu_tab, **button_style)
        view_menu_btn.pack(fill='x', pady=5)
        
        feedback_btn = tk.Button(self.left_panel, text="Submit Feedback", 
                               command=self.show_feedback_tab, **button_style)
        feedback_btn.pack(fill='x', pady=5)
        
        # Exit button
        exit_btn = tk.Button(self.left_panel, text="Exit", 
                           command=self.root.destroy,
                           font=('Helvetica', 12), bg='#a0754b', fg='white', 
                           activebackground='#a0754b', activeforeground='white',
                           relief='flat', bd=0, padx=10, pady=10)
        exit_btn.pack(fill='x', pady=(40, 5))
    
    def clear_right_panel(self):
        """Clear all widgets from the right panel"""
        for widget in self.right_panel.winfo_children():
            if widget != self.bg_label if hasattr(self, 'bg_label') else True:
                widget.destroy()
    
    def show_order_tab(self):
        """Show the order tab in the right panel"""
        self.clear_right_panel()
        
        # Create a container frame in the right panel
        container = tk.Frame(self.right_panel, bg='white', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        
        # Main frames
        left_frame = ttk.Frame(container)
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        right_frame = ttk.Frame(container)
        right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        # ===== LEFT FRAME - MENU ITEMS =====
        ttk.Label(left_frame, text="Menu Items", font=('Helvetica', 12, 'bold')).pack(pady=5)
        
        # Create notebook for different meal times
        self.menu_notebook = ttk.Notebook(left_frame)
        self.menu_notebook.pack(fill='both', expand=True)
        
        # Create tabs for each meal time
        self.breakfast_tab = ttk.Frame(self.menu_notebook)
        self.brunch_tab = ttk.Frame(self.menu_notebook)
        self.lunch_tab = ttk.Frame(self.menu_notebook)
        self.dinner_tab = ttk.Frame(self.menu_notebook)
        
        self.menu_notebook.add(self.breakfast_tab, text='Breakfast')
        self.menu_notebook.add(self.brunch_tab, text='Brunch')
        self.menu_notebook.add(self.lunch_tab, text='Lunch')
        self.menu_notebook.add(self.dinner_tab, text='Dinner')
        
        # Create treeviews for each tab
        self.create_menu_treeview(self.breakfast_tab)
        self.create_menu_treeview(self.brunch_tab)
        self.create_menu_treeview(self.lunch_tab)
        self.create_menu_treeview(self.dinner_tab)
        
        # Load menu items
        self.load_menu_items()
        
        # ===== RIGHT FRAME - ORDER FORM =====
        # Customer Email
        ttk.Label(right_frame, text="Customer Email:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.order_customer_email = ttk.Entry(right_frame)
        self.order_customer_email.grid(row=0, column=1, padx=5, pady=5)
        
        # Dish ID (now populated from selected menu item)
        ttk.Label(right_frame, text="Dish ID:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.order_dish_id = ttk.Entry(right_frame, state='normal')
        self.order_dish_id.grid(row=1, column=1, padx=5, pady=5)
        
        # Quantity
        ttk.Label(right_frame, text="Quantity:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.order_quantity = ttk.Spinbox(right_frame, from_=1, to=100)
        self.order_quantity.grid(row=2, column=1, padx=5, pady=5)
        self.order_quantity.set(1)
        
        # Order Date
        ttk.Label(right_frame, text="Order Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.order_date = ttk.Entry(right_frame)
        self.order_date.grid(row=3, column=1, padx=5, pady=5)
        self.order_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Delivery Address
        ttk.Label(right_frame, text="Delivery Address:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.order_address = ttk.Entry(right_frame)
        self.order_address.grid(row=4, column=1, padx=5, pady=5)
        
        # Payment Method
        ttk.Label(right_frame, text="Payment Method:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.order_payment = ttk.Combobox(right_frame, values=["Credit Card", "Debit Card", "PayPal", "Cash on Delivery"])
        self.order_payment.grid(row=5, column=1, padx=5, pady=5)
        self.order_payment.current(0)
        
        # Place Order Button
        ttk.Button(right_frame, text="Place Order", command=self.place_order).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Display Bill Button (initially disabled)
        self.display_bill_btn = ttk.Button(right_frame, text="Display Bill", 
                                         state="disabled", command=self.display_bill)
        self.display_bill_btn.grid(row=7, column=0, columnspan=2, pady=10)
        
        # Result Label
        self.order_result = ttk.Label(right_frame, text="", foreground="red")
        self.order_result.grid(row=8, column=0, columnspan=2)
        
        # Configure grid weights
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

    def show_reservation_tab(self):
        """Show the reservation tab in the right panel"""
        self.clear_right_panel()
        
        # Create a container frame in the right panel
        container = tk.Frame(self.right_panel, bg='white', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        
        # Left Frame for reservation form
        reservation_frame = ttk.Frame(container)
        reservation_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Customer Email
        ttk.Label(reservation_frame, text="Customer Email:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.res_customer_email = ttk.Entry(reservation_frame)
        self.res_customer_email.grid(row=0, column=1, padx=5, pady=5)
        
        # Table ID
        ttk.Label(reservation_frame, text="Table ID:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.res_table_id = ttk.Entry(reservation_frame)
        self.res_table_id.grid(row=1, column=1, padx=5, pady=5)
        
        # Reservation Date
        ttk.Label(reservation_frame, text="Reservation Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.res_date = ttk.Entry(reservation_frame)
        self.res_date.grid(row=2, column=1, padx=5, pady=5)
        self.res_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Time Slot
        ttk.Label(reservation_frame, text="Time Slot:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.res_time_slot = ttk.Combobox(reservation_frame, 
                                        values=["Breakfast", "Lunch", "Dinner", "Evening"])
        self.res_time_slot.grid(row=3, column=1, padx=5, pady=5)
        self.res_time_slot.current(1)  # Default to Lunch
        
        # Reserve Button
        ttk.Button(reservation_frame, text="Reserve Table", 
                 command=self.reserve_table).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Result Label
        self.res_result = ttk.Label(reservation_frame, text="", foreground="red")
        self.res_result.grid(row=5, column=0, columnspan=2)
        
        # Right Frame for available tables
        available_tables_frame = ttk.LabelFrame(container, text="Available Tables")
        available_tables_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        # Treeview for available tables
        self.tables_tree = ttk.Treeview(available_tables_frame, columns=('ID', 'Capacity', 'Location'), show='headings')
        self.tables_tree.heading('ID', text='Table ID')
        self.tables_tree.heading('Capacity', text='Capacity')
        self.tables_tree.heading('Location', text='Location')
        self.tables_tree.column('ID', width=50)
        self.tables_tree.column('Capacity', width=70)
        self.tables_tree.column('Location', width=100)
        
        scrollbar = ttk.Scrollbar(available_tables_frame, orient="vertical", command=self.tables_tree.yview)
        self.tables_tree.configure(yscrollcommand=scrollbar.set)
        
        self.tables_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button to refresh available tables
        ttk.Button(available_tables_frame, text="Refresh Tables", 
                 command=self.load_available_tables).pack(pady=5)
        
        # Configure grid weights
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Load available tables
        self.load_available_tables()

    def show_feedback_tab(self):
        """Show the feedback tab in the right panel"""
        self.clear_right_panel()
        
        # Create a container frame in the right panel
        container = tk.Frame(self.right_panel, bg='white', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        
        # Customer Email
        ttk.Label(container, text="Customer Email:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.feedback_customer_email = ttk.Entry(container)
        self.feedback_customer_email.grid(row=0, column=1, padx=5, pady=5)
        
        # Table ID
        ttk.Label(container, text="Table ID:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.feedback_table_id = ttk.Entry(container)
        self.feedback_table_id.grid(row=1, column=1, padx=5, pady=5)
        
        # Reservation ID
        ttk.Label(container, text="Reservation ID:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.feedback_reservation_id = ttk.Entry(container)
        self.feedback_reservation_id.grid(row=2, column=1, padx=5, pady=5)
        
        # Reservation Date
        ttk.Label(container, text="Reservation Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.feedback_reservation_date = ttk.Entry(container)
        self.feedback_reservation_date.grid(row=3, column=1, padx=5, pady=5)
        self.feedback_reservation_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Feedback Details
        ttk.Label(container, text="Feedback:").grid(row=4, column=0, padx=5, pady=5, sticky="ne")
        self.feedback_details = tk.Text(container, height=5, width=30)
        self.feedback_details.grid(row=4, column=1, padx=5, pady=5)
        
        # Rating
        ttk.Label(container, text="Rating (1-5):").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.feedback_rating = ttk.Spinbox(container, from_=1, to=5)
        self.feedback_rating.grid(row=5, column=1, padx=5, pady=5)
        self.feedback_rating.set(5)  # Default to highest rating
        
        # Submit Button
        ttk.Button(container, text="Submit Feedback", 
                 command=self.submit_feedback).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Result Label
        self.feedback_result = ttk.Label(container, text="", foreground="red")
        self.feedback_result.grid(row=7, column=0, columnspan=2)

    def show_view_menu_tab(self):
        """Show the view menu tab in the right panel"""
        self.clear_right_panel()
        
        # Create a container frame in the right panel
        container = tk.Frame(self.right_panel, bg='white', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        
        # Create a container frame with scrollbar
        scroll_container = ttk.Frame(container)
        scroll_container.pack(fill='both', expand=True)
        
        # Create a canvas for scrolling
        self.menu_canvas = tk.Canvas(scroll_container)
        self.menu_canvas.pack(side='left', fill='both', expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(scroll_container, orient='vertical', command=self.menu_canvas.yview)
        scrollbar.pack(side='right', fill='y')
        self.menu_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame inside canvas to hold menu sections
        self.menu_frame = ttk.Frame(self.menu_canvas)
        self.menu_canvas.create_window((0, 0), window=self.menu_frame, anchor='nw')
        
        # Bind the canvas to configure scroll region
        self.menu_frame.bind('<Configure>', lambda e: self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox('all')))
        
        # Button to refresh menu
        refresh_btn = ttk.Button(container, text="Refresh Menu", command=self.load_menu_sections)
        refresh_btn.pack(pady=5)
        
        # Load menu sections initially
        self.load_menu_sections()

    # ===== ALL THE REST OF THE METHODS REMAIN THE SAME =====
    # (place_order, display_bill, reserve_table, submit_feedback, etc.)
    # Just copy all the remaining methods from your original code without changes

    def test_connection(self, silent=False):
        try:
            conn = oracledb.connect(
                user=self.conn_username.get(),
                password=self.conn_password.get(),
                dsn=self.conn_dsn.get()
            )
            conn.close()
            if not silent:
                messagebox.showinfo("Success", "Connection successful!")
            return True
        except Exception as e:
            if not silent:
                messagebox.showerror("Error", f"Connection failed: {str(e)}")
            return False

    def load_menu_sections(self):
        """Load all menu sections (Breakfast, Brunch, Lunch, Dinner)"""
        if not self.test_connection(silent=True):
            messagebox.showerror("Error", "Database connection failed")
            return
        
        # Clear existing menu items
        for widget in self.menu_frame.winfo_children():
            widget.destroy()
        
        try:
            conn = oracledb.connect(
                user=self.conn_username.get(),
                password=self.conn_password.get(),
                dsn=self.conn_dsn.get()
            )
            cursor = conn.cursor()
            
            # Load Breakfast menu
            self.create_menu_section("Breakfast", cursor)
            
            # Load Brunch menu
            self.create_menu_section("Brunch", cursor)
            
            # Load Lunch menu
            self.create_menu_section("Lunch", cursor)
            
            # Load Dinner menu
            self.create_menu_section("Dinner", cursor)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load menu: {str(e)}")
    
    def create_menu_section(self, category, cursor):
        """Create a menu section for a specific category"""
        # Section header
        header_frame = ttk.Frame(self.menu_frame, borderwidth=2, relief='groove')
        header_frame.pack(fill='x', padx=5, pady=10)
        
        ttk.Label(header_frame, text=category, font=('Helvetica', 14, 'bold')).pack(pady=5)
        
        # Get menu items for this category
        cursor.execute(f"""
            SELECT m.DISHID, d.NAME, d.PRICE, m.DESCRIPTION, m.AVAILABILITY
            FROM {category.upper()}_MENU m
            JOIN DISH_P d ON m.DISHID = d.DISHID
            ORDER BY m.DISHID
        """)
        
        items = cursor.fetchall()
        
        if not items:
            ttk.Label(header_frame, text="No items available", font=('Helvetica', 10, 'italic')).pack(pady=5)
            return
        
        # Create treeview for menu items
        tree_frame = ttk.Frame(header_frame)
        tree_frame.pack(fill='x', padx=10, pady=5)
        
        tree = ttk.Treeview(tree_frame, columns=('id', 'name', 'price', 'description', 'availability'), 
                           show='headings', height=min(len(items), 10))
        
        # Configure columns
        tree.heading('id', text='Dish ID')
        tree.heading('name', text='Name')
        tree.heading('price', text='Price')
        tree.heading('description', text='Description')
        tree.heading('availability', text='Available')
        
        tree.column('id', width=80, anchor='center')
        tree.column('name', width=150, anchor='w')
        tree.column('price', width=80, anchor='e')
        tree.column('description', width=200, anchor='w')
        tree.column('availability', width=80, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        tree.pack(side='left', fill='x', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Add items to treeview
        for item in items:
            availability = "Yes" if item[4] == 'Y' else "No"
            tree.insert("", "end", values=(item[0], item[1], f"${item[2]:.2f}", item[3], availability))

    def create_menu_treeview(self, parent_frame):
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(parent_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Create treeview
        tree = ttk.Treeview(tree_frame, columns=('dishid', 'name', 'price', 'description'), show='headings', height=10)
        
        # Configure columns
        tree.heading('dishid', text='Dish ID')
        tree.heading('name', text='Name')
        tree.heading('price', text='Price')
        tree.heading('description', text='Description')
        
        tree.column('dishid', width=80, anchor='center')
        tree.column('name', width=150, anchor='w')
        tree.column('price', width=80, anchor='e')
        tree.column('description', width=200, anchor='w')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        tree.bind('<<TreeviewSelect>>', lambda event: self.on_menu_item_selected(tree, event))
        
        # Store reference to the treeview
        if parent_frame == self.breakfast_tab:
            self.breakfast_tree = tree
        elif parent_frame == self.brunch_tab:
            self.brunch_tree = tree
        elif parent_frame == self.lunch_tab:
            self.lunch_tree = tree
        elif parent_frame == self.dinner_tab:
            self.dinner_tree = tree

    def on_menu_item_selected(self, tree, event):
        selected_item = tree.focus()
        if selected_item:
            item_data = tree.item(selected_item)
            dish_id = item_data['values'][0]  # First column is dishid
            self.order_dish_id.config(state='normal')
            self.order_dish_id.delete(0, tk.END)
            self.order_dish_id.insert(0, dish_id)
            self.order_dish_id.config(state='readonly')

    def load_menu_items(self):
        if not self.test_connection(silent=True):
            messagebox.showerror("Error", "Database connection failed")
            return
        
        try:
            conn = oracledb.connect(
                user=self.conn_username.get(),
                password=self.conn_password.get(),
                dsn=self.conn_dsn.get()
            )
            cursor = conn.cursor()
            
            # Clear existing items
            for tree in [self.breakfast_tree, self.brunch_tree, self.lunch_tree, self.dinner_tree]:
                for item in tree.get_children():
                    tree.delete(item)
            
            # Load Breakfast items
            cursor.execute("""
                SELECT m.DISHID, d.NAME, d.PRICE, m.DESCRIPTION
                FROM BREAKFAST_MENU m
                JOIN DISH_P d ON m.DISHID = d.DISHID
                WHERE m.AVAILABILITY = 'Y'
            """)
            for row in cursor:
                self.breakfast_tree.insert("", "end", values=row)
            
            # Load Brunch items
            cursor.execute("""
                SELECT m.DISHID, d.NAME, d.PRICE, m.DESCRIPTION
                FROM BRUNCH_MENU m
                JOIN DISH_P d ON m.DISHID = d.DISHID
                WHERE m.AVAILABILITY = 'Y'
            """)
            for row in cursor:
                self.brunch_tree.insert("", "end", values=row)
            
            # Load Lunch items
            cursor.execute("""
                SELECT m.DISHID, d.NAME, d.PRICE, m.DESCRIPTION
                FROM LUNCH_MENU m
                JOIN DISH_P d ON m.DISHID = d.DISHID
                WHERE m.AVAILABILITY = 'Y'
            """)
            for row in cursor:
                self.lunch_tree.insert("", "end", values=row)
            
            # Load Dinner items
            cursor.execute("""
                SELECT m.DISHID, d.NAME, d.PRICE, m.DESCRIPTION
                FROM DINNER_MENU m
                JOIN DISH_P d ON m.DISHID = d.DISHID
                WHERE m.AVAILABILITY = 'Y'
            """)
            for row in cursor:
                self.dinner_tree.insert("", "end", values=row)
            
            # Auto-select the appropriate tab based on current time
            current_hour = datetime.now().hour
            if 6 <= current_hour < 11:
                self.menu_notebook.select(self.breakfast_tab)
            elif 11 <= current_hour < 14:
                self.menu_notebook.select(self.brunch_tab)
            elif 14 <= current_hour < 17:
                self.menu_notebook.select(self.lunch_tab)
            else:
                self.menu_notebook.select(self.dinner_tab)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load menu items: {str(e)}")

    def place_order(self):
        if not self.test_connection(silent=True):
            messagebox.showerror("Error", "Database connection failed")
            return
            
        try:
            # Get all order details
            customer_email = self.order_customer_email.get().strip()
            dish_id = self.order_dish_id.get().strip()
            quantity = int(self.order_quantity.get())
            order_date = self.order_date.get().strip()
            address = self.order_address.get().strip()
            payment_method = self.order_payment.get().strip()
            
            # Validate inputs
            if not all([customer_email, dish_id, order_date, address]):
                self.order_result.config(text="❌ All fields are required", foreground="red")
                return
            
            if quantity <= 0:
                self.order_result.config(text="❌ Quantity must be positive", foreground="red")
                return
            
            # Get database connection
            conn = oracledb.connect(
                user=self.conn_username.get(),
                password=self.conn_password.get(),
                dsn=self.conn_dsn.get()
            )
            cursor = conn.cursor()
            
            # 1. Check if customer exists
            cursor.execute("SELECT customerid FROM customer_P WHERE email = :email", {'email': customer_email})
            customer_result = cursor.fetchone()
            
            if not customer_result:
                self.order_result.config(text="❌ Customer not found", foreground="red")
                cursor.close()
                conn.close()
                return
            
            customer_id = customer_result[0]
            
            # 2. Check if dish exists and get price
            cursor.execute("SELECT price FROM Dish_P WHERE dishid = :dish_id", {'dish_id': dish_id})
            dish_result = cursor.fetchone()
            
            if not dish_result:
                self.order_result.config(text="❌ Dish not found", foreground="red")
                cursor.close()
                conn.close()
                return
            
            price = dish_result[0]
            total_amount = price * quantity
            
            try:
                # Temporarily disable the trigger causing the mutation error
                cursor.execute("ALTER TRIGGER SYSTEM.CALCULATE_ORDER_TOTAL DISABLE")
                
                # 3. Insert into order_P table
                order_query = """
                    INSERT INTO order_P (customerid, orderdate, totalamount, delivery_address, payment_method)
                    VALUES (:customerid, TO_DATE(:orderdate, 'YYYY-MM-DD'), :totalamount, :address, :payment_method)
                    RETURNING orderid INTO :order_id
                """
                
                order_id_var = cursor.var(oracledb.NUMBER)
                cursor.execute(order_query, {
                    'customerid': customer_id,
                    'orderdate': order_date,
                    'totalamount': total_amount,
                    'address': address,
                    'payment_method': payment_method,
                    'order_id': order_id_var
                })
                
                order_id = order_id_var.getvalue()[0]
                
                # 4. Insert into order_details_P table
                order_item_query = """
                    INSERT INTO order_details_P (orderid, dishid, quantity, price_per_unit)
                    VALUES (:orderid, :dishid, :quantity, :price)
                """
                
                cursor.execute(order_item_query, {
                    'orderid': order_id,
                    'dishid': dish_id,
                    'quantity': quantity,
                    'price': price
                })
                
                # Re-enable the trigger after operations are complete
                cursor.execute("ALTER TRIGGER SYSTEM.CALCULATE_ORDER_TOTAL ENABLE")
                
                conn.commit()
                
                self.order_result.config(text=f"✅ Order placed successfully! Order ID: {order_id}", foreground="green")
                
                # Store the order ID for bill generation
                self.last_order_id = order_id
                self.display_bill_btn.config(state="normal")
                
                # Clear form
                self.order_dish_id.delete(0, tk.END)
                self.order_quantity.set(1)
                self.order_address.delete(0, tk.END)
                
            except oracledb.DatabaseError as e:
                # If trigger disable fails, try without disabling
                error_obj = e.args[0]
                if error_obj.code == 4043:  # Trigger doesn't exist
                    # Retry the operations without disabling the trigger
                    cursor.execute(order_query, {
                        'customerid': customer_id,
                        'orderdate': order_date,
                        'totalamount': total_amount,
                        'address': address,
                        'payment_method': payment_method,
                        'order_id': order_id_var
                    })
                    
                    order_id = order_id_var.getvalue()[0]
                    
                    cursor.execute(order_item_query, {
                        'orderid': order_id,
                        'dishid': dish_id,
                        'quantity': quantity,
                        'price': price
                    })
                    
                    conn.commit()
                    
                    self.order_result.config(text=f"✅ Order placed successfully! Order ID: {order_id}", foreground="green")
                    self.last_order_id = order_id
                    self.display_bill_btn.config(state="normal")
                    self.order_dish_id.delete(0, tk.END)
                    self.order_quantity.set(1)
                    self.order_address.delete(0, tk.END)
                else:
                    conn.rollback()
                    self.order_result.config(text=f"❌ Error placing order: {error_obj.message}", foreground="red")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.order_result.config(text=f"❌ Error placing order: {str(e)}", foreground="red")

    def display_bill(self):
        if not self.test_connection(silent=True) or not self.last_order_id:
            messagebox.showerror("Error", "No valid order ID found or connection failed")
            return
            
        try:
            conn = oracledb.connect(
                user=self.conn_username.get(),
                password=self.conn_password.get(),
                dsn=self.conn_dsn.get()
            )
            cursor = conn.cursor()
            
            # 1. Get order details
            cursor.execute("""
                SELECT o.orderid, o.orderdate, o.totalamount, o.payment_method, 
                       c.name, c.email, c.contact, o.delivery_address
                FROM order_P o
                JOIN customer_P c ON o.customerid = c.customerid
                WHERE o.orderid = :order_id
            """, {'order_id': self.last_order_id})
            
            order_info = cursor.fetchone()
            
            if not order_info:
                messagebox.showerror("Error", "Order not found")
                return
                    
            (order_id, order_date, total_amount, payment_method, 
             customer_name, customer_email, customer_phone, delivery_address) = order_info
            
                        # 2. Get order items
            cursor.execute("""
                SELECT d.name, od.quantity, od.price_per_unit, 
                       (od.quantity * od.price_per_unit) as item_total
                FROM order_details_P od
                JOIN dish_P d ON od.dishid = d.dishid
                WHERE od.orderid = :order_id
                ORDER BY od.orderid
            """, {'order_id': self.last_order_id})
            
            order_items = cursor.fetchall()
            
            if not order_items:
                messagebox.showerror("Error", "No items found for this order")
                return
            
            # 3. Calculate financials
            discount_percent = 5 if total_amount > 100 else 0
            discount_amount = total_amount * (discount_percent / 100)
            subtotal = total_amount - discount_amount
            tax_rate = 0.10  # 10% sales tax
            tax_amount = subtotal * tax_rate
            grand_total = subtotal + tax_amount
            
            # 4. Generate bill in database
            try:
                bill_id_var = cursor.var(oracledb.NUMBER)
                
                cursor.execute("""
                    INSERT INTO bill_P (orderid, customerid, paymentmethod, billdate, 
                                      subtotal, discount, tax, paidamount)
                    VALUES (:orderid, 
                           (SELECT customerid FROM order_P WHERE orderid = :orderid),
                           :paymentmethod, 
                           SYSDATE, 
                           :subtotal, 
                           :discount,
                           :tax,
                           :paidamount)
                    RETURNING billid INTO :bill_id
                """, {
                    'orderid': order_id,
                    'paymentmethod': payment_method,
                    'subtotal': subtotal,
                    'discount': discount_amount,
                    'tax': tax_amount,
                    'paidamount': grand_total,
                    'bill_id': bill_id_var
                })
                
                bill_id = bill_id_var.getvalue()[0]
                conn.commit()
                
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")
                return
            
            # 5. Create bill window
            bill_window = tk.Toplevel(self.root)
            bill_window.title(f"Invoice #INV-{bill_id:05d}")
            bill_window.geometry("700x850")
            
            # Main container
            main_frame = ttk.Frame(bill_window, padding=20)
            main_frame.pack(fill='both', expand=True)
            
            # ===== HEADER SECTION =====
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill='x', pady=(0, 15))
            
            # Restaurant info
            ttk.Label(header_frame, text="Gourmet Delights Restaurant", 
                     font=('Helvetica', 16, 'bold')).pack()
            ttk.Label(header_frame, text="123 Food Street, Culinary City", 
                     font=('Helvetica', 10)).pack()
            ttk.Label(header_frame, text="Phone: (555) 123-4567 | Tax ID: TX-987654321", 
                     font=('Helvetica', 9)).pack()
            
            # Invoice title
            ttk.Label(main_frame, text="TAX INVOICE", 
                     font=('Helvetica', 14, 'bold')).pack(pady=10)
            
            # ===== BILL INFO SECTION =====
            info_frame = ttk.Frame(main_frame)
            info_frame.pack(fill='x', pady=10)
            
            # Left column - Invoice details
            invoice_frame = ttk.Frame(info_frame)
            invoice_frame.pack(side='left', fill='x', expand=True)
            
            ttk.Label(invoice_frame, text=f"Invoice #: INV-{bill_id:05d}", anchor='w').pack(fill='x')
            ttk.Label(invoice_frame, text=f"Order #: ORD-{order_id:05d}", anchor='w').pack(fill='x')
            ttk.Label(invoice_frame, text=f"Date: {order_date}", anchor='w').pack(fill='x')
            ttk.Label(invoice_frame, text=f"Payment: {payment_method}", anchor='w').pack(fill='x')
            
            # Right column - Customer details
            customer_frame = ttk.Frame(info_frame)
            customer_frame.pack(side='right', fill='x', expand=True)
            
            ttk.Label(customer_frame, text="Customer Details:", 
                     font=('Helvetica', 9, 'bold'), anchor='w').pack(fill='x')
            ttk.Label(customer_frame, text=f"{customer_name}", anchor='w').pack(fill='x')
            ttk.Label(customer_frame, text=f"{customer_email}", anchor='w').pack(fill='x')
            ttk.Label(customer_frame, text=f"{customer_phone}", anchor='w').pack(fill='x')
            ttk.Label(customer_frame, text=f"Address: {delivery_address}", anchor='w').pack(fill='x')
            
            # Separator
            ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
            
            # ===== ORDER ITEMS SECTION =====
            ttk.Label(main_frame, text="Order Items", 
                     font=('Helvetica', 11, 'bold')).pack(anchor='w')
            
            # Treeview for items
            columns = ("item", "qty", "price", "total")
            tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=6)
            
            # Configure columns
            tree.heading("item", text="Item")
            tree.heading("qty", text="Qty")
            tree.heading("price", text="Unit Price")
            tree.heading("total", text="Total")
            
            tree.column("item", width=200, anchor='w')
            tree.column("qty", width=50, anchor='center')
            tree.column("price", width=100, anchor='e')
            tree.column("total", width=100, anchor='e')
            
            # Add items
            for item in order_items:
                tree.insert("", "end", values=(
                    item[0],        # Name
                    item[1],        # Quantity
                    f"${item[2]:.2f}",  # Price
                    f"${item[3]:.2f}"   # Total
                ))
            
            tree.pack(fill='x', pady=5)
            
            # ===== PAYMENT SUMMARY SECTION =====
            ttk.Label(main_frame, text="Payment Summary", 
                     font=('Helvetica', 11, 'bold')).pack(anchor='w', pady=(15, 5))
            
            summary_frame = ttk.Frame(main_frame)
            summary_frame.pack(fill='x')
            
            # Summary rows
            rows = [
                ("Subtotal:", f"${total_amount:.2f}"),
                (f"Discount ({discount_percent}%):", f"-${discount_amount:.2f}"),
                ("Sales Tax (10%):", f"${tax_amount:.2f}"),
                ("Total Amount:", f"${grand_total:.2f}", 'bold')
            ]
            
            for i, (label, value, *style) in enumerate(rows):
                font = ('Helvetica', 9, 'bold') if 'bold' in style else ('Helvetica', 9)
                ttk.Label(summary_frame, text=label, font=font).grid(row=i, column=0, sticky='e')
                ttk.Label(summary_frame, text=value, font=font).grid(row=i, column=1, padx=10, sticky='e')
            
            # Configure grid
            summary_frame.columnconfigure(0, weight=1)
            
            # ===== FOOTER SECTION =====
            ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)
            
            footer_frame = ttk.Frame(main_frame)
            footer_frame.pack(fill='x')
            
            ttk.Label(footer_frame, text="Thank you for dining with us!", 
                     font=('Helvetica', 10, 'italic')).pack()
            ttk.Label(footer_frame, text="* Terms & Conditions Apply").pack()
            
            # Action buttons
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(pady=20)
            
            ttk.Button(btn_frame, text="Print Invoice", 
                      command=lambda: self.print_bill(bill_window)).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Close", 
                      command=bill_window.destroy).pack(side='left', padx=5)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")

    def print_bill(self, window):
        """Placeholder for print functionality"""
        messagebox.showinfo("Print", "Bill sent to printer")
        window.focus_set()

    def load_available_tables(self):
        if not self.test_connection(silent=True):
            messagebox.showerror("Error", "Database connection failed")
            return
        
        try:
            conn = oracledb.connect(
                user=self.conn_username.get(),
                password=self.conn_password.get(),
                dsn=self.conn_dsn.get()
            )
            cursor = conn.cursor()
            
            # Clear existing data
            for item in self.tables_tree.get_children():
                self.tables_tree.delete(item)
            
            # Get available tables
            cursor.execute("""
                SELECT TABLEID, CAPACITY, LOCATION 
                FROM TABLE_INFO_P 
                WHERE BOOKING_STAT = 'Available'
                ORDER BY TABLEID
            """)
            
            for row in cursor:
                self.tables_tree.insert("", "end", values=row)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load available tables: {str(e)}")
    
    def reserve_table(self):
        if not self.test_connection(silent=True):
            messagebox.showerror("Error", "Database connection failed")
            return
            
        try:
            # Get all reservation details
            customer_email = self.res_customer_email.get().strip()
            table_id = self.res_table_id.get().strip()
            reservation_date = self.res_date.get().strip()
            time_slot = self.res_time_slot.get().strip()
            
            # Validate inputs
            if not all([customer_email, table_id, reservation_date, time_slot]):
                self.res_result.config(text="❌ All fields are required", foreground="red")
                return
            
            # Get database connection
            conn = oracledb.connect(
                user=self.conn_username.get(),
                password=self.conn_password.get(),
                dsn=self.conn_dsn.get()
            )
            cursor = conn.cursor()
            
            # 1. Check if customer exists and get customer ID
            cursor.execute("SELECT customerid FROM customer_P WHERE email = :email", {'email': customer_email})
            customer_result = cursor.fetchone()
            
            if not customer_result:
                self.res_result.config(text="❌ Customer not found", foreground="red")
                cursor.close()
                conn.close()
                return
            
            customer_id = customer_result[0]
            
            # 2. Call the reserve_table procedure
            try:
                # Prepare the procedure call
                procedure_call = """
                    BEGIN
                        reserve_table(
                            p_customer_id => :customer_id,
                            p_table_id => :table_id,
                            p_reservation_date => TO_DATE(:res_date, 'YYYY-MM-DD'),
                            p_time_slot => :time_slot
                        );
                    END;
                """
                
                # Execute the procedure
                cursor.execute(procedure_call, {
                    'customer_id': customer_id,
                    'table_id': table_id,
                    'res_date': reservation_date,
                    'time_slot': time_slot
                })
                
                conn.commit()
                
                self.res_result.config(text="✅ Table reserved successfully!", foreground="green")
                
                # Clear form
                self.res_table_id.delete(0, tk.END)
                
                # Refresh available tables
                self.load_available_tables()
                
            except oracledb.DatabaseError as e:
                error_obj = e.args[0]
                self.res_result.config(text=f"❌ Error reserving table: {error_obj.message}", foreground="red")
                conn.rollback()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.res_result.config(text=f"❌ Error reserving table: {str(e)}", foreground="red")

    def submit_feedback(self):
        if not self.test_connection(silent=True):
            messagebox.showerror("Error", "Database connection failed")
            return
            
        try:
            # Get all feedback details
            customer_email = self.feedback_customer_email.get().strip()
            table_id = self.feedback_table_id.get().strip()
            reservation_id = self.feedback_reservation_id.get().strip()
            reservation_date = self.feedback_reservation_date.get().strip()
            feedback_details = self.feedback_details.get("1.0", "end-1c").strip()
            rating = int(self.feedback_rating.get())
            
            # Validate inputs
            if not all([customer_email, table_id, reservation_id, reservation_date, feedback_details]):
                self.feedback_result.config(text="❌ All fields are required", foreground="red")
                return
            
            if rating < 1 or rating > 5:
                self.feedback_result.config(text="❌ Rating must be between 1 and 5", foreground="red")
                return
            
            # Get database connection
            conn = oracledb.connect(
                user=self.conn_username.get(),
                password=self.conn_password.get(),
                dsn=self.conn_dsn.get()
            )
            cursor = conn.cursor()
            
            # 1. Check if customer exists and get customer ID
            cursor.execute("SELECT customerid FROM customer_P WHERE email = :email", {'email': customer_email})
            customer_result = cursor.fetchone()
            
            if not customer_result:
                self.feedback_result.config(text="❌ Customer not found", foreground="red")
                cursor.close()
                conn.close()
                return
            
            customer_id = customer_result[0]
            
            # 2. Call the take_feedback procedure
            try:
                # Prepare the procedure call
                procedure_call = """
                    BEGIN
                        take_feedback(
                            p_customer_id => :customer_id,
                            p_table_id => :table_id,
                            p_reservation_id => :reservation_id,
                            p_reservation_date => TO_DATE(:reservation_date, 'YYYY-MM-DD'),
                            p_feedback_details => :feedback_details,
                            p_rating => :rating
                        );
                    END;
                """
                
                # Execute the procedure
                cursor.execute(procedure_call, {
                    'customer_id': customer_id,
                    'table_id': table_id,
                    'reservation_id': reservation_id,
                    'reservation_date': reservation_date,
                    'feedback_details': feedback_details,
                    'rating': rating
                })
                
                conn.commit()
                
                self.feedback_result.config(text="✅ Feedback submitted successfully!", foreground="green")
                
                # Clear form
                self.feedback_details.delete("1.0", tk.END)
                
            except oracledb.DatabaseError as e:
                error_obj = e.args[0]
                self.feedback_result.config(text=f"❌ Error submitting feedback: {error_obj.message}", foreground="red")
                conn.rollback()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.feedback_result.config(text=f"❌ Error submitting feedback: {str(e)}", foreground="red")

    def open_admin_panel(self):
        if not self.test_connection(silent=True):
            messagebox.showerror("Error", "Database connection failed")
            return
            
        connection_params = {
            'username': self.conn_username.get(),
            'password': self.conn_password.get(),
            'dsn': self.conn_dsn.get()
        }
        

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseTester(root)
    root.mainloop()