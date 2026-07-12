import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from Customer_Auth import CustomerAuth
from p import DatabaseTester as Customer
from AdminAuth import AdminAuth  # Import AdminAuth

from p3 import open_staff_panel
from p2 import SupplierManager

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f1d8b3")
        
        self.connection_params = {
            'username': "system",
            'password': "Layby9898",
            'dsn': "localhost:1521/orcl1"
        }

        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        try:
            self.bg_image = PhotoImage(file="bg.png")
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.canvas.configure(bg="#f1d8b3")
        
        button_frame = tk.Frame(self.canvas, bg="#f1d8b3", bd=2, relief="ridge")
        button_frame.place(relx=0.4, rely=0.5, anchor="center", width=400, height=500)
        
        tk.Label(button_frame, text="Welcome to", font=('Helvetica', 18), bg="#f1d8b3", fg="#a0754b").pack(pady=(30, 5))
        tk.Label(button_frame, text="RESTAURANT", font=('Helvetica', 24, 'bold'), bg="#f1d8b3", fg="#a0754b").pack()
        tk.Label(button_frame, text="MANAGEMENT SYSTEM", font=('Helvetica', 14), bg="#f1d8b3", fg="#a0754b").pack(pady=(0, 30))
        
        button_style = {
            'bg': "#ffffff", 
            'fg': "#a0754b", 
            'font': ('Helvetica', 12, 'bold'),
            'width': 20,
            'pady': 10,
            'bd': 0,
            'activebackground': "#a0754b",
            'activeforeground': "#ffffff"
        }
        
        tk.Button(button_frame, text="Customer", command=self.customer_login, **button_style).pack(pady=10, fill='x')
        tk.Button(button_frame, text="Admin", command=self.admin_login, **button_style).pack(pady=10, fill='x')
        tk.Button(button_frame, text="Staff Login", command=self.staff_login, **button_style).pack(pady=10, fill='x')
        tk.Button(button_frame, text="Supplier Login", command=self.supplier_login, **button_style).pack(pady=10, fill='x')
    
    def customer_login(self):
        customer_window = tk.Toplevel(self.root)
        CustomerAuth(customer_window)
    
    def admin_login(self):
        admin_window = tk.Toplevel(self.root)
        AdminAuth(admin_window, self.connection_params)
    
    def staff_login(self):
        open_staff_panel(self.connection_params)
    
    def supplier_login(self):
        supplier_window = tk.Toplevel(self.root)
        SupplierManager(supplier_window, self.connection_params)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()