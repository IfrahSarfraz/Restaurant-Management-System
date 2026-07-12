import tkinter as tk
from tkinter import ttk, messagebox
import oracledb
import hashlib
from tkinter import PhotoImage
import os

class SupplierManager:
    def __init__(self, root, connection_params):
        self.root = root
        self.root.title("Supplier Management System")
        self.root.geometry("1000x800")
        
        self.connection_params = connection_params
        self.conn = None
        self.supplier_id = None
        self.supplier_info = None
        self.bg_image = None

        # Create main container
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True)
        
        # Create canvas for background
        self.canvas = tk.Canvas(self.main_container)
        self.canvas.pack(fill='both', expand=True)
        
        # Load background image
        self.load_background_image()
        
        # Create login frame (no tabs)
        self.create_login_frame()
        
        if not self.connect_to_db():
            messagebox.showerror("Error", "Failed to connect to database")
            self.root.destroy()

    def load_background_image(self):
        """Load and display background image with proper scaling"""
        try:
            # Use absolute path to ensure the image is found
            base_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(base_dir, "bg.png")
            
            self.bg_image = PhotoImage(file=image_path)
            self.bg_img = self.canvas.create_image(0, 0, image=self.bg_image, anchor='nw')
            self.canvas.bind('<Configure>', self.resize_background)
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.canvas.configure(bg="#f5f5f5")

    def resize_background(self, event):
        """Resize background image to window size"""
        if self.bg_image:
            self.canvas.coords(self.bg_img, event.width//400, event.height//400)

    def configure_styles(self):
        """Configure custom styles"""
        self.style = ttk.Style()
        self.style.configure('TButton', 
                           background="#a0754b", 
                           foreground="white",
                           font=('Helvetica', 10, 'bold'),
                           borderwidth=0)
        self.style.map('TButton', 
                      background=[('active', '#8a6540')])

    def connect_to_db(self):
        try:
            self.conn = oracledb.connect(
                user=self.connection_params['username'],
                password=self.connection_params['password'],
                dsn=self.connection_params['dsn']
            )
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to database: {str(e)}")
            return False

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_login_frame(self):
        """Create the login frame"""
        # Main frame with shadow effect
        self.login_frame = tk.Frame(self.canvas, bg="white", bd=0, highlightthickness=0)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=350)
        
        # Title
        title_label = tk.Label(self.login_frame, text="Supplier Login", 
                             font=('Helvetica', 18, 'bold'), 
                             bg="white", fg="#333333")
        title_label.pack(pady=(25, 20))
        
        # Email
        email_frame = tk.Frame(self.login_frame, bg="white")
        email_frame.pack(pady=(0, 15), padx=20, fill='x')
        tk.Label(email_frame, text="Email:", bg="white", 
                font=('Helvetica', 12)).pack(side="left", padx=(0, 10))
        self.login_email = tk.Entry(email_frame, bd=1, relief="solid", 
                                 font=('Helvetica', 12),
                                 highlightthickness=1, 
                                 highlightcolor="#cccccc", 
                                 highlightbackground="#cccccc")
        self.login_email.pack(side="right", expand=True, fill='x')
        
        # Password
        pass_frame = tk.Frame(self.login_frame, bg="white")
        pass_frame.pack(pady=(0, 25), padx=20, fill='x')
        tk.Label(pass_frame, text="Password:", bg="white", 
                font=('Helvetica', 12)).pack(side="left", padx=(0, 10))
        self.login_password = tk.Entry(pass_frame, show="*", bd=1, relief="solid", 
                                     font=('Helvetica', 12),
                                     highlightthickness=1, 
                                     highlightcolor="#cccccc", 
                                     highlightbackground="#cccccc")
        self.login_password.pack(side="right", expand=True, fill='x')
        
        # Divider line
        tk.Frame(self.login_frame, height=1, bg="#eeeeee").pack(fill="x", padx=20, pady=5)
        
        # Login button (brown with white text)
        login_btn = tk.Button(self.login_frame, text="Login", command=self.supplier_login,
                            bg="#a0754b", fg="white", font=('Helvetica', 12, 'bold'),
                            padx=30, pady=8, bd=0, activebackground="#8a6540",
                            activeforeground="white")
        login_btn.pack(pady=(10, 15))
        
        # Sign up button
        signup_btn = tk.Button(self.login_frame, text="Don't have an account? Sign Up", 
                             command=self.show_signup,
                             bg="white", fg="#a0754b", font=('Helvetica', 10),
                             bd=0, activebackground="#f1d8b3")
        signup_btn.pack()
        
        # Status label
        self.login_result = tk.Label(self.login_frame, text="", 
                                   font=('Helvetica', 10), bg="white")
        self.login_result.pack(pady=(10, 0))

    def show_signup(self):
        """Show the signup frame"""
        self.login_frame.place_forget()
        
        # Main frame with shadow effect
        self.signup_frame = tk.Frame(self.canvas, bg="white", bd=0, highlightthickness=0)
        self.signup_frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=500)
        
        # Title
        title_label = tk.Label(self.signup_frame, text="Supplier Signup", 
                             font=('Helvetica', 18, 'bold'), 
                             bg="white", fg="#333333")
        title_label.pack(pady=(20, 15))
        
        # Fields
        fields = [
            ("Company Name*", "companyname", False, False),
            ("Contact Name", "name", False, False),
            ("Email*", "email", False, False),
            ("Password*", "password", True, False),
            ("Confirm Password*", "confirm_password", True, False),
            ("Address*", "address", False, False),
            ("Contact Details", "contactdetails", False, True)
        ]
        
        self.entries = {}
        
        for i, (label_text, field_name, is_password, is_textarea) in enumerate(fields):
            frame = tk.Frame(self.signup_frame, bg="white")
            frame.pack(fill='x', padx=20, pady=5)
            
            tk.Label(frame, text=label_text, bg="white", 
                    font=('Helvetica', 10)).pack(side="left", padx=(0, 10))
            
            if is_textarea:
                entry = tk.Text(frame, height=4, width=30, 
                              font=('Helvetica', 10),
                              wrap=tk.WORD, padx=5, pady=5,
                              highlightthickness=1, 
                              highlightcolor="#cccccc", 
                              highlightbackground="#cccccc")
                entry.pack(side="right", expand=True, fill='x')
            elif is_password:
                entry = tk.Entry(frame, show="*" if is_password else None, 
                               font=('Helvetica', 10),
                               highlightthickness=1, 
                               highlightcolor="#cccccc", 
                               highlightbackground="#cccccc")
                entry.pack(side="right", expand=True, fill='x')
            else:
                entry = tk.Entry(frame, font=('Helvetica', 10),
                               highlightthickness=1, 
                               highlightcolor="#cccccc", 
                               highlightbackground="#cccccc")
                entry.pack(side="right", expand=True, fill='x')
            
            self.entries[field_name] = entry
        
        # Divider line
        tk.Frame(self.signup_frame, height=1, bg="#eeeeee").pack(fill="x", padx=20, pady=5)
        
        # Create Account button (brown with white text)
        create_btn = tk.Button(self.signup_frame, text="Create Account", 
                             command=self.create_supplier_account,
                             bg="#a0754b", fg="white", font=('Helvetica', 12, 'bold'),
                             padx=30, pady=8, bd=0, activebackground="#8a6540",
                             activeforeground="white")
        create_btn.pack(pady=(10, 15))
        
        # Back to login button
        back_btn = tk.Button(self.signup_frame, text="Already have an account? Login", 
                           command=self.show_login,
                           bg="white", fg="#a0754b", font=('Helvetica', 10),
                           bd=0, activebackground="#f1d8b3")
        back_btn.pack()
        
        # Status label
        self.signup_result = tk.Label(self.signup_frame, text="", 
                                    font=('Helvetica', 10), bg="white")
        self.signup_result.pack(pady=(10, 0))

    def show_login(self):
        """Show the login frame"""
        if hasattr(self, 'signup_frame'):
            self.signup_frame.place_forget()
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=350)

    def supplier_login(self):
        """Handle supplier login and switch to dashboard"""
        email = self.login_email.get().strip()
        password = self.login_password.get().strip()
        
        if not email or not password:
            self.login_result.config(text="❌ Email and password are required", foreground="red")
            return
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT supplierid, companyname, name, email, address, contactdetails, registrationdate 
                FROM SYSTEM.SUPPLIER_P 
                WHERE email = :email AND password = :password
            """, {
                'email': email,
                'password': self.hash_password(password)
            })
            
            supplier = cursor.fetchone()
            
            if supplier:
                self.supplier_id = int(supplier[0])
                self.supplier_info = {
                    'company': supplier[1],
                    'name': supplier[2],
                    'email': supplier[3],
                    'address': supplier[4],
                    'contactdetails': supplier[5],
                    'regdate': supplier[6]
                }
                
                # Close login window and open dashboard
                self.root.destroy()
                self.open_dashboard()
            else:
                self.login_result.config(text="❌ Invalid email or password", foreground="red")
            
            cursor.close()
        except oracledb.DatabaseError as e:
            error_obj = e.args[0]
            self.login_result.config(text=f"❌ Database error: {error_obj.message}", foreground="red")
        except Exception as e:
            self.login_result.config(text=f"❌ Error: {str(e)}", foreground="red")

    def create_supplier_account(self):
        """Create new supplier account"""
        company = self.entries['companyname'].get().strip()
        name = self.entries['name'].get().strip()
        email = self.entries['email'].get().strip()
        password = self.entries['password'].get().strip()
        confirm = self.entries['confirm_password'].get().strip()
        address = self.entries['address'].get().strip()
        contactdetails = self.entries['contactdetails'].get("1.0", tk.END).strip()
        
        if not all([company, email, password, confirm, address]):
            self.signup_result.config(text="❌ All required fields (*) must be filled", foreground="red")
            return
            
        if password != confirm:
            self.signup_result.config(text="❌ Passwords don't match", foreground="red")
            return
            
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM SYSTEM.SUPPLIER_P WHERE email = :email", {'email': email})
            if cursor.fetchone()[0] > 0:
                self.signup_result.config(text="❌ Email already registered", foreground="red")
                return
            
            cursor.execute("""
                INSERT INTO SYSTEM.SUPPLIER_P (
                    companyname, name, email, password, address, contactdetails
                ) VALUES (
                    :company, :name, :email, :password, :address, :contactdetails
                )
            """, {
                'company': company,
                'name': name if name else None,
                'email': email,
                'password': self.hash_password(password),
                'address': address,
                'contactdetails': contactdetails if contactdetails else None
            })
            
            self.conn.commit()
            self.signup_result.config(text="✅ Account created successfully! Please login.", foreground="green")
            
            # Clear all fields
            for entry in self.entries.values():
                if isinstance(entry, tk.Text):
                    entry.delete("1.0", tk.END)
                else:
                    entry.delete(0, tk.END)
            
            # Switch back to login
            self.show_login()
            
        except oracledb.DatabaseError as e:
            error_obj = e.args[0]
            self.signup_result.config(text=f"❌ Database error: {error_obj.message}", foreground="red")
            self.conn.rollback()
        except Exception as e:
            self.signup_result.config(text=f"❌ Error: {str(e)}", foreground="red")
            self.conn.rollback()
        finally:
            cursor.close()

    def open_dashboard(self):
        """Open the dashboard window with background image"""
        dashboard = tk.Tk()
        dashboard.title("Supplier Dashboard")
        dashboard.geometry("1200x800")
        
        # Create main container
        main_container = tk.Frame(dashboard)
        main_container.pack(fill='both', expand=True)
        
        # Create canvas for background
        canvas = tk.Canvas(main_container)
        canvas.pack(fill='both', expand=True)
        
        # Load background image
        try:
            bg_image = PhotoImage(file="bg.png")
            bg_img = canvas.create_image(0, 0, image=bg_image, anchor='nw')
            canvas.bind('<Configure>', lambda e: canvas.coords(bg_img, e.width//2, e.height//2))
        except Exception as e:
            print(f"Error loading background image: {e}")
            canvas.configure(bg="#f5f5f5")
        
        # Main content frame (skin color with transparent sides)
        content_frame = tk.Frame(canvas, bg="#f1d8b3", bd=0)
        content_frame.place(relx=0.5, rely=0.5, anchor="center", width=1100, height=700)
        
        # Notebook for tabs
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Profile tab
        profile_tab = ttk.Frame(notebook)
        notebook.add(profile_tab, text='My Profile')
        self.create_profile_tab(profile_tab)
        
        # Orders tab
        orders_tab = ttk.Frame(notebook)
        notebook.add(orders_tab, text='My Orders')
        self.create_orders_tab(orders_tab)
        
        # Logout button
        logout_btn = tk.Button(content_frame, text="Logout", 
                             command=dashboard.destroy,
                             bg="#a0754b", fg="white", 
                             font=('Helvetica', 10, 'bold'),
                             padx=20, pady=5, bd=0,
                             activebackground="#8a6540",
                             activeforeground="white")
        logout_btn.pack(side='bottom', pady=10)
        
        dashboard.mainloop()

    def create_profile_tab(self, parent):
        """Create profile information tab"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        ttk.Label(scrollable_frame, 
                 text="Supplier Profile Information", 
                 font=('Helvetica', 16, 'bold')).grid(
                     row=0, column=0, columnspan=2, pady=(10, 20))
        
        # Info fields
        info_labels = [
            ("Supplier ID:", f"{self.supplier_id}"),
            ("Company Name:", self.supplier_info['company']),
            ("Contact Name:", self.supplier_info['name'] or "Not provided"),
            ("Email Address:", self.supplier_info['email']),
            ("Physical Address:", self.supplier_info['address']),
            ("Registration Date:", self.supplier_info['regdate'].strftime("%Y-%m-%d %H:%M:%S")),
            ("Contact Details:", self.supplier_info['contactdetails'] or "Not provided")
        ]
        
        for i, (label_text, value) in enumerate(info_labels, start=1):
            ttk.Label(scrollable_frame, 
                     text=label_text, 
                     font=('Helvetica', 12, 'bold'),
                     anchor="e").grid(
                         row=i, column=0, sticky="e", padx=10, pady=5)
            
            if label_text == "Contact Details:" and self.supplier_info['contactdetails']:
                details_frame = ttk.Frame(scrollable_frame)
                details_frame.grid(row=i, column=1, sticky="w", padx=10, pady=5)
                
                details_text = tk.Text(details_frame, 
                                     height=5, 
                                     width=50, 
                                     wrap=tk.WORD,
                                     font=('Helvetica', 10),
                                     padx=5, pady=5)
                details_text.insert("1.0", value)
                details_text.config(state='disabled')
                details_text.pack(fill='both', expand=True)
            else:
                ttk.Label(scrollable_frame, 
                         text=value,
                         font=('Helvetica', 12)).grid(
                             row=i, column=1, sticky="w", padx=10, pady=5)

    def create_orders_tab(self, parent):
        """Create orders tab"""
        try:
            cursor = self.conn.cursor()
            
            # Check if supplier has any orders
            cursor.execute("""
                SELECT COUNT(*) 
                FROM SYSTEM.SUPPLIER_ORDERS 
                WHERE SUPPLIERID = :supplier_id
            """, {'supplier_id': self.supplier_id})
            order_count = cursor.fetchone()[0]
            
            if order_count > 0:
                # Get full order details
                cursor.execute("""
                    SELECT ORDERID, TO_CHAR(ORDERDATE, 'YYYY-MM-DD HH24:MI'), STATUS, DETAILS 
                    FROM SYSTEM.SUPPLIER_ORDERS 
                    WHERE SUPPLIERID = :supplier_id
                    ORDER BY ORDERDATE DESC
                """, {'supplier_id': self.supplier_id})
                
                orders = cursor.fetchall()
                
                main_frame = ttk.Frame(parent)
                main_frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Treeview for orders list
                tree_frame = ttk.Frame(main_frame)
                tree_frame.pack(fill='both', expand=True)
                
                tree = ttk.Treeview(tree_frame, 
                                  columns=('ID', 'Date', 'Status'), 
                                  show='headings',
                                  selectmode='browse')
                tree.heading('ID', text='Order ID')
                tree.heading('Date', text='Order Date')
                tree.heading('Status', text='Status')
                
                # Add scrollbars
                vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
                hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
                tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
                
                tree.grid(row=0, column=0, sticky='nsew')
                vsb.grid(row=0, column=1, sticky='ns')
                hsb.grid(row=1, column=0, sticky='ew')
                
                # Add orders to treeview
                for order in orders:
                    tree.insert('', 'end', values=(order[0], order[1], order[2]))
                
                # Configure grid weights
                tree_frame.grid_columnconfigure(0, weight=1)
                tree_frame.grid_rowconfigure(0, weight=1)
                
                # Order details frame
                details_frame = ttk.LabelFrame(main_frame, text="Order Details")
                details_frame.pack(fill='both', expand=True, pady=(10, 0))
                
                details_text = tk.Text(details_frame, 
                                     height=10, 
                                     wrap=tk.WORD,
                                     font=('Helvetica', 10),
                                     padx=5, pady=5)
                details_text.pack(fill='both', expand=True, padx=5, pady=5)
                details_text.config(state='disabled')
                
                # Show order details when selected
                def show_order_details(event):
                    selected = tree.focus()
                    if selected:
                        order_id = tree.item(selected)['values'][0]
                        for order in orders:
                            if order[0] == order_id:
                                details_text.config(state='normal')
                                details_text.delete('1.0', tk.END)
                                details_text.insert('1.0', order[3] or "No additional details available")
                                details_text.config(state='disabled')
                                break
                
                tree.bind('<<TreeviewSelect>>', show_order_details)
                
                # Select first order by default
                if len(tree.get_children()) > 0:
                    tree.selection_set(tree.get_children()[0])
                    tree.focus(tree.get_children()[0])
                    tree.event_generate('<<TreeviewSelect>>')
            else:
                # No orders message
                ttk.Label(parent, 
                         text="No orders found for your account\n\n"
                              "If you believe this is incorrect, please:\n"
                              "1. Verify your orders in the database\n"
                              "2. Check your supplier ID matches\n"
                              "3. Contact support",
                         font=('Helvetica', 12),
                         justify='center').pack(pady=50)
            
            cursor.close()
        except oracledb.DatabaseError as e:
            error_obj = e.args[0]
            messagebox.showerror("Database Error", 
                               f"Failed to load orders:\n{error_obj.message}\n(Code: {error_obj.code})")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")

def open_supplier_panel(connection_params):
    root = tk.Tk()
    SupplierManager(root, connection_params)
    root.mainloop()

if __name__ == "__main__":
    connection_params = {
        'username': 'system',
        'password': 'Layby9898',
        'dsn': 'localhost:1521/orcl1'
    }
    open_supplier_panel(connection_params)