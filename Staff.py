import tkinter as tk
from tkinter import ttk, messagebox
import oracledb
from PIL import Image, ImageTk

class StaffPanel:
    def __init__(self, root, connection_params):
        self.root = root
        self.root.title("Staff Dashboard")
        self.root.geometry("1200x700")
        
        self.connection_params = connection_params
        self.conn = None
        self.current_staff = None
        
        # Create main container
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True)
        
        # Left Panel (Navigation)
        self.left_panel = tk.Frame(self.main_container, width=250, bg="#f1d8b3")
        self.left_panel.pack(side='left', fill='y')
        self.left_panel.pack_propagate(False)
        
        # Right Panel (Content)
        self.right_panel = tk.Frame(self.main_container, bg="#cdffd8")
        self.right_panel.pack(side='right', fill='both', expand=True)
        
        # Add title to left panel
        title_label = tk.Label(
            self.left_panel, 
            text="STAFF PANEL", 
            font=('Helvetica', 18, 'bold'), 
            bg="#f1d8b3", 
            fg="white",
            pady=20
        )
        title_label.pack(fill='x')
        
        # Create navigation buttons
        self.create_navigation_buttons()
        
        # Dictionary to hold content frames
        self.content_frames = {}
        
        # Create all content frames immediately
        self.create_login_content()
        self.create_order_details_content()
        
        # Initially show welcome content
        self.show_welcome_content()
        
        # Test connection
        self.test_connection()

    def create_navigation_buttons(self):
        # Create buttons
        self.create_button("LOGIN", "login", top_margin=20)
        self.create_button("ORDER DETAILS", "order_details")
        
        # Add separator
        tk.Frame(self.left_panel, height=2, bg="#a0754b").pack(fill='x', pady=20)
        
        # Logout button (only shown when logged in)
        self.logout_btn = tk.Button(
            self.left_panel,
            text="LOGOUT",
            font=('Helvetica', 10),
            bg="#a0754b",
            fg="white",
            activebackground="#a0754b",
            activeforeground="white",
            bd=0,
            padx=20,
            pady=10,
            anchor='w',
            command=self.logout
        )
        self.logout_btn.pack(fill='x', pady=(5, 5))
        self.logout_btn.pack_forget()  # Hide initially
    
    def create_button(self, text, command_key, top_margin=0):
        button = tk.Button(
            self.left_panel,
            text=text,
            font=('Helvetica', 10),
            bg="#a0754b",
            fg="white",
            activebackground="#a0754b",
            activeforeground="white",
            bd=0,
            padx=20,
            pady=10,
            anchor='w',
            command=lambda: self.show_content(command_key)
        )
        button.pack(fill='x', pady=(top_margin, 5))
    
    def show_welcome_content(self):
        # Hide all frames first
        for frame in self.content_frames.values():
            frame.pack_forget()
        
        # Clear right panel (in case any widgets exist outside frames)
        for widget in self.right_panel.winfo_children():
            if widget not in self.content_frames.values():
                widget.destroy()
        
        # Show welcome message
        welcome_frame = tk.Frame(self.right_panel, bg="#cdffd8")
        welcome_frame.pack(fill='both', expand=True)
        
        welcome_label = tk.Label(
            welcome_frame,
            text="Welcome to Staff Dashboard\n\nPlease select an option from the left menu",
            font=('Helvetica', 24),
            bg="#cdffd8",
            fg="#2c3e50"
        )
        welcome_label.pack(expand=True)
        
        # Store temporary welcome frame
        self.welcome_frame = welcome_frame
    
    def show_content(self, content_key):
        # Hide welcome frame if it exists
        if hasattr(self, 'welcome_frame'):
            self.welcome_frame.pack_forget()
        
        # Hide all content frames first
        for frame in self.content_frames.values():
            frame.pack_forget()
        
        # Show the selected content if it exists
        if content_key in self.content_frames:
            self.content_frames[content_key].pack(fill='both', expand=True)
            
            # If showing order details and logged in, load data
            if content_key == "order_details" and self.current_staff:
                self.safe_tree_update(self.load_order_details)
    
    def create_login_content(self):
        # Create login frame
        frame = tk.Frame(self.right_panel, bg="#cdffd8")
        
        # Title
        title = tk.Label(
            frame,
            text="STAFF LOGIN",
            font=('Helvetica', 18, 'bold'),
            bg="#cdffd8",
            fg="#2c3e50",
            pady=20
        )
        title.pack(fill='x')
        
        # Login form container
        form_frame = tk.Frame(frame, bg="#cdffd8")
        form_frame.pack(expand=True)
        
        # Staff ID
        id_frame = tk.Frame(form_frame, bg="#cdffd8")
        id_frame.pack(pady=(0, 15), padx=50, fill='x')
        tk.Label(id_frame, text="Staff ID:", font=('Helvetica', 12), 
                bg="#cdffd8", fg="#2c3e50").pack(side="left")
        self.staff_id_entry = ttk.Entry(id_frame, font=('Helvetica', 12))
        self.staff_id_entry.pack(side="right", expand=True, fill='x', padx=(10, 0))
        
        # Password
        pass_frame = tk.Frame(form_frame, bg="#ecf0f1")
        pass_frame.pack(pady=(0, 25), padx=50, fill='x')
        tk.Label(pass_frame, text="Password:", font=('Helvetica', 12), 
                bg="#cdffd8", fg="#2c3e50").pack(side="left")
        self.password_entry = ttk.Entry(pass_frame, show="*", font=('Helvetica', 12))
        self.password_entry.pack(side="right", expand=True, fill='x', padx=(10, 0))
        
        # Login button
        login_btn = tk.Button(form_frame, text="Login", command=self.staff_login,
                            bg="#f1d8b3", fg="white", font=('Helvetica', 12, 'bold'),
                            width=15, pady=5, bd=0, activebackground="#27ae60")
        login_btn.pack(pady=(20, 10))
        
        # Store the frame
        self.content_frames["login"] = frame
    
    def create_order_details_content(self):
        # Create order details frame
        frame = tk.Frame(self.right_panel, bg="#cdffd8")
        
        # Title
        title = tk.Label(
            frame,
            text="ORDER MANAGEMENT",
            font=('Helvetica', 18, 'bold'),
            bg="#cdffd8",
            fg="#2c3e50",
            pady=10
        )
        title.pack(fill='x')
        
        # Treeview frame
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Scrollbars
        h_scroll = ttk.Scrollbar(tree_frame, orient='horizontal')
        h_scroll.pack(side='bottom', fill='x')
        
        v_scroll = ttk.Scrollbar(tree_frame)
        v_scroll.pack(side='right', fill='y')
        
        # Treeview
        columns = ["Order ID", "Customer ID", "Dish Name", "Description", "Status"]
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=15,
            xscrollcommand=h_scroll.set,
            yscrollcommand=v_scroll.set
        )
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        
        # Specific column adjustments
        self.tree.column("Dish Name", width=200, anchor='w')
        self.tree.column("Description", width=250, anchor='w')
        
        self.tree.pack(side='left', fill='both', expand=True)
        h_scroll.config(command=self.tree.xview)
        v_scroll.config(command=self.tree.yview)
        
        # Controls frame
        controls_frame = tk.Frame(frame, bg="#cdffd8")
        controls_frame.pack(fill='x', pady=(5, 10), padx=20)
        
        # Refresh button
        refresh_btn = tk.Button(controls_frame, text="Refresh Orders", 
                              command=lambda: self.safe_tree_update(self.load_order_details),
                              bg="#3498db", fg="white", 
                              font=('Helvetica', 10, 'bold'),
                              width=15, pady=3, bd=0, 
                              activebackground="#2980b9")
        refresh_btn.pack(side='left', padx=5)
        
        # Status filter
        tk.Label(controls_frame, text="Filter by Status:", 
                bg="#ecf0f1", fg="#2c3e50", 
                font=('Helvetica', 10)).pack(side='left', padx=5)
        
        self.status_filter = ttk.Combobox(controls_frame, 
                                        values=["All", "Pending", "Preparing", "Ready", "Delivered"],
                                        font=('Helvetica', 10))
        self.status_filter.pack(side='left', padx=5)
        self.status_filter.set("All")
        
        # Filter button
        filter_btn = tk.Button(controls_frame, text="Apply Filter", 
                             command=lambda: self.safe_tree_update(
                                 lambda: self.filter_orders(self.status_filter.get())),
                             bg="#3498db", fg="white", 
                             font=('Helvetica', 10, 'bold'),
                             width=15, pady=3, bd=0, 
                             activebackground="#2980b9")
        filter_btn.pack(side='left', padx=5)
        
        # Store the frame
        self.content_frames["order_details"] = frame
    
    def test_connection(self):
        """Test database connection"""
        try:
            self.conn = oracledb.connect(
                user=self.connection_params['username'],
                password=self.connection_params['password'],
                dsn=self.connection_params['dsn']
            )
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", f"Database connection failed: {str(e)}")
            return False

    def staff_login(self):
        """Handle staff login"""
        staff_id = self.staff_id_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not staff_id or not password:
            messagebox.showerror("Error", "Both Staff ID and Password are required")
            return
            
        try:
            staff_id = int(staff_id)  
        except ValueError:
            messagebox.showerror("Error", "Staff ID must be a number")
            return
            
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT STAFFID, S_NAME, STAFFROLE
                FROM STAFF_P
                WHERE STAFFID = :staff_id AND PASSWORD = :password
            """, {
                'staff_id': staff_id,
                'password': password
            })
            
            result = cursor.fetchone()
            
            if result:
                self.current_staff = {
                    'id': result[0],
                    'name': result[1],
                    'role': result[2]
                }
                messagebox.showinfo("Login Successful", 
                                  f"Welcome, {self.current_staff['name']} ({self.current_staff['role']})")
                
                # Show logout button
                self.logout_btn.pack(fill='x', pady=(5, 5))
                
                # Show order details content
                self.show_content("order_details")
            else:
                messagebox.showerror("Login Failed", "Invalid Staff ID or Password")
                
            cursor.close()
                
        except oracledb.DatabaseError as e:
            error = e.args[0]
            messagebox.showerror("Database Error", f"Error {error.code}: {error.message}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")

    def safe_tree_update(self, callback):
        """Safely update treeview after checking existence"""
        if hasattr(self, 'tree') and self.tree.winfo_exists():
            callback()
        else:
            self.root.after(100, lambda: self.safe_tree_update(callback))

    def load_order_details(self):
        """Load order details"""
        if not self.current_staff:
            messagebox.showerror("Error", "Please login first")
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM ORDER_DETAILS_VIEW ORDER BY ORDERID")
            
            # Clear existing items
            self.tree.delete(*self.tree.get_children())
            
            for row in cursor:
                self.tree.insert("", "end", values=row)
            
            cursor.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")

    def filter_orders(self, status):
        """Filter orders by status"""
        if not self.current_staff:
            messagebox.showerror("Error", "Please login first")
            return
            
        try:
            cursor = self.conn.cursor()
            
            if status == "All":
                cursor.execute("SELECT * FROM ORDER_DETAILS_VIEW ORDER BY ORDERID")
            else:
                cursor.execute("""
                    SELECT * FROM ORDER_DETAILS_VIEW 
                    WHERE STATUS = :status 
                    ORDER BY ORDERID
                """, {'status': status})
            
            # Clear existing items
            self.tree.delete(*self.tree.get_children())
            
            for row in cursor:
                self.tree.insert("", "end", values=row)
            
            cursor.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter orders: {str(e)}")
    
    def logout(self):
        """Handle logout"""
        self.current_staff = None
        self.staff_id_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.show_welcome_content()
        self.logout_btn.pack_forget()
        messagebox.showinfo("Logged Out", "You have been successfully logged out")

def open_staff_panel(connection_params):
    root = tk.Tk()
    StaffPanel(root, connection_params)
    root.mainloop()

if __name__ == "__main__":
    test_params = {
        'username': "system",
        'password': "Layby9898",
        'dsn': "localhost:1521/orcl1"
    }
    open_staff_panel(test_params)