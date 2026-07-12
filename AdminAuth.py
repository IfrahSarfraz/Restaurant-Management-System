import tkinter as tk
from tkinter import ttk, messagebox
import oracledb
import hashlib
from tkinter import PhotoImage
import p1

class AdminAuth:
    def __init__(self, root, connection_params):  # Fixed: Changed from init to __init__
        self.root = root
        self.root.title("Admin Authentication")
        self.root.geometry("1200x700")  
        self.root.configure(bg="#f1d8b3")  
        
        # Store connection parameters
        self.connection_params = connection_params
        self.conn = None
        
        # Create a canvas for the background image
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        try:
            # Load background image
            self.bg_image = PhotoImage(file="bg.png")
            # Resize image to window size while maintaining aspect ratio
            self.bg_image = self.bg_image.zoom(2)
            self.bg_image = self.bg_image.subsample(1)
            
            # Add image to canvas
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except Exception as e:
            print(f"Error loading background image: {e}")
            # Fallback to solid color background
            self.canvas.configure(bg="#f1d8b3")
        
        # Create a main frame for the authentication content
        self.main_frame = tk.Frame(self.canvas, bg="#f1d8b3", bd=2, relief="ridge")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=400)
        
        # Show login form by default
        self.show_login_form()
        
        # Test connection
        self.test_connection()
    
    def test_connection(self):
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
    
    def show_login_form(self):
        """Show the admin login form"""
        # Clear any existing widgets
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Login form
        tk.Label(self.main_frame, text="Admin Login", font=('Helvetica', 18, 'bold'), 
                bg="#f1d8b3", fg="#a0754b").pack(pady=(20, 10))
        
        # Username field
        username_frame = tk.Frame(self.main_frame, bg="#f1d8b3")
        username_frame.pack(pady=10)
        tk.Label(username_frame, text="Username:", font=('Helvetica', 12), 
                bg="#f1d8b3", fg="#a0754b").pack(side="left", padx=(0, 10))
        self.login_username = ttk.Entry(username_frame, font=('Helvetica', 12))
        self.login_username.pack(side="left")
        
        # Password field
        password_frame = tk.Frame(self.main_frame, bg="#f1d8b3")
        password_frame.pack(pady=10)
        tk.Label(password_frame, text="Password:", font=('Helvetica', 12), 
                bg="#f1d8b3", fg="#a0754b").pack(side="left", padx=(0, 10))
        self.login_password = ttk.Entry(password_frame, show="*", font=('Helvetica', 12))
        self.login_password.pack(side="left")
        
        # Login button
        login_btn = tk.Button(self.main_frame, text="Login", command=self.admin_login,
                            bg="#ffffff", fg="#a0754b", font=('Helvetica', 12, 'bold'),
                            width=15, pady=5, bd=0, activebackground="#a0754b",
                            activeforeground="#ffffff")
        login_btn.pack(pady=20)
        
        # Status label
        self.login_status = tk.Label(self.main_frame, text="", font=('Helvetica', 11),
                                   bg="#f1d8b3", fg="red")
        self.login_status.pack()
    
    def admin_login(self):  # Fixed: Properly indented to be part of the class
        """Handle admin login"""
        if not self.conn:
            messagebox.showerror("Error", "No database connection")
            return
            
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        
        if not username or not password:
            self.login_status.config(text="Username and password are required", foreground="red")
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Hash the provided password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Check if admin exists
            query = """
                SELECT adminid, name FROM admin_p 
                WHERE username = :username AND password = :password
            """
            cursor.execute(query, {'username': username, 'password': hashed_password})
            result = cursor.fetchone()
            
            if result:
                admin_id, admin_name = result
                self.login_status.config(text=f"Login successful! Welcome {admin_name}", fg="green")
                
                # Close the cursor and connection
                cursor.close()
                self.conn.close()
                
                # Destroy the current window properly
                self.root.destroy()
                
                # Create a new root window for the admin panel
                new_root = tk.Tk()
                p1.AdminPanel(new_root, self.connection_params)
                new_root.mainloop()
                
            else:
                self.login_status.config(text="Invalid username or password", fg="red")
                cursor.close()
            
        except Exception as e:
            self.login_status.config(text=f"Login failed: {str(e)}", fg="red")
            if 'cursor' in locals():
                cursor.close()

def open_admin_auth(connection_params):
    root = tk.Tk()
    AdminAuth(root, connection_params)
    root.mainloop()

if __name__ == "__main__":  # Fixed: Changed from name to __name__
    # For testing the admin authentication standalone
    connection_params = {
        'username': 'system',
        'password': 'Layby9898',
        'dsn': 'localhost:1521/orcl1'
    }
    open_admin_auth(connection_params)