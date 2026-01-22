import os
import csv
import datetime as dt
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter
import hashlib
import json

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# -----------------------------
# Authentication System
# -----------------------------

class AuthManager:
    """Handles user authentication and password management"""
    
    def __init__(self):
        self.users_file = "users.csv"
        self.session_file = "session.json"
        self.current_user = None
        self._init_users_file()
        
    def _init_users_file(self):
        """Initialize users file if it doesn't exist"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["username", "password_hash", "full_name", "created_at"])
                # Create default admin user (password: admin123)
                admin_hash = self._hash_password("admin123")
                writer.writerow(["admin", admin_hash, "Administrator", dt.datetime.now().isoformat()])
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, password: str, full_name: str) -> Tuple[bool, str]:
        """Register a new user"""
        # Validate inputs
        if not username or not password or not full_name:
            return False, "All fields are required"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Check if username already exists
        users = self._load_users()
        if username in users:
            return False, "Username already exists"
        
        # Add new user
        password_hash = self._hash_password(password)
        with open(self.users_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([username, password_hash, full_name, dt.datetime.now().isoformat()])
        
        return True, "Registration successful"
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, str]:
        """Authenticate user credentials"""
        if not username or not password:
            return False, "Username and password required"
        
        users = self._load_users()
        if username not in users:
            return False, "Invalid username or password"
        
        password_hash = self._hash_password(password)
        if users[username]["password_hash"] != password_hash:
            return False, "Invalid username or password"
        
        self.current_user = {
            "username": username,
            "full_name": users[username]["full_name"]
        }
        self._save_session()
        return True, "Login successful"
    
    def _load_users(self) -> Dict:
        """Load all users from file"""
        users = {}
        try:
            with open(self.users_file, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    users[row["username"]] = {
                        "password_hash": row["password_hash"],
                        "full_name": row["full_name"],
                        "created_at": row["created_at"]
                    }
        except FileNotFoundError:
            pass
        return users
    
    def _save_session(self):
        """Save current session"""
        if self.current_user:
            with open(self.session_file, "w") as f:
                json.dump(self.current_user, f)
    
    def load_session(self) -> bool:
        """Load saved session if exists"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, "r") as f:
                    self.current_user = json.load(f)
                return True
        except:
            pass
        return False
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
    
    def get_current_user(self) -> Optional[Dict]:
        """Get currently logged in user"""
        return self.current_user


class LoginWindow(tk.Tk):
    """Login/Registration Window"""
    
    def __init__(self):
        super().__init__()
        self.auth_manager = AuthManager()
        self.authenticated = False
        self.user_data = None
        
        # Hide window initially to prevent flashing
        self.withdraw()
        
        self.title("🔐 Expense Manager - Login")
        self.geometry("550x700")
        self.configure(bg="#1a1a2e")
        self.resizable(False, False)
        
        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"550x700+{x}+{y}")
        
        self._build_ui()
        
        # Show window after everything is built
        self.deiconify()
        
    def _build_ui(self):
        """Build login UI"""
        # Header with gradient effect
        header_frame = tk.Frame(self, bg="#0f3460", height=120)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Title with shadow effect
        title_container = tk.Frame(header_frame, bg="#0f3460")
        title_container.pack(expand=True)
        
        tk.Label(title_container, text="💰 Expense Manager", 
                font=("Segoe UI", 28, "bold"), fg="#00d4ff", bg="#0f3460").pack()
        tk.Label(title_container, text="Smart Financial Tracking", 
                font=("Segoe UI", 11), fg="#94a3b8", bg="#0f3460").pack()
        
        # Main container with modern styling
        main_frame = tk.Frame(self, bg="#1a1a2e")
        main_frame.pack(fill="both", expand=True, padx=50, pady=30)
        
        # Custom styled notebook
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Custom.TNotebook', background="#1a1a2e", borderwidth=0)
        style.configure('Custom.TNotebook.Tab', 
                       background="#16213e", 
                       foreground="#94a3b8",
                       padding=[20, 10],
                       font=("Segoe UI", 11, "bold"))
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', '#0f3460')],
                 foreground=[('selected', '#00d4ff')])
        
        self.notebook = ttk.Notebook(main_frame, style='Custom.TNotebook')
        self.notebook.pack(fill="both", expand=True)
        
        # Login Tab
        login_frame = tk.Frame(self.notebook, bg="#16213e")
        self.notebook.add(login_frame, text="🔓  Login")
        self._build_login_tab(login_frame)
        
        # Register Tab
        register_frame = tk.Frame(self.notebook, bg="#16213e")
        self.notebook.add(register_frame, text="✨  Register")
        self._build_register_tab(register_frame)
        
        # Footer with modern styling
        footer_frame = tk.Frame(self, bg="#1a1a2e", height=60)
        footer_frame.pack(fill="x")
        footer_frame.pack_propagate(False)
        
        tk.Label(footer_frame, text="💡 Default credentials: admin / admin123", 
                font=("Segoe UI", 10), fg="#64748b", bg="#1a1a2e").pack(pady=10)
        tk.Label(footer_frame, text="Secure • Fast • Intuitive", 
                font=("Segoe UI", 9, "italic"), fg="#475569", bg="#1a1a2e").pack()
    
    def _build_login_tab(self, parent):
        """Build login form"""
        container = tk.Frame(parent, bg="#16213e")
        container.pack(expand=True, padx=40, pady=40)
        
        # Welcome text
        tk.Label(container, text="Welcome Back!", 
                font=("Segoe UI", 20, "bold"), fg="#00d4ff", bg="#16213e").pack(pady=(0, 30))
        
        # Username field with modern styling
        tk.Label(container, text="👤 Username", 
                font=("Segoe UI", 11, "bold"), fg="#cbd5e1", bg="#16213e").pack(anchor="w", pady=(0, 8))
        
        username_frame = tk.Frame(container, bg="#0f3460", highlightbackground="#1e40af", highlightthickness=2)
        username_frame.pack(fill="x", pady=(0, 20))
        self.login_username = tk.Entry(username_frame, font=("Segoe UI", 12), bg="#0f3460", 
                                      fg="white", relief="flat", insertbackground="white", bd=10)
        self.login_username.pack(fill="x")
        
        # Password field
        tk.Label(container, text="🔒 Password", 
                font=("Segoe UI", 11, "bold"), fg="#cbd5e1", bg="#16213e").pack(anchor="w", pady=(0, 8))
        
        password_frame = tk.Frame(container, bg="#0f3460", highlightbackground="#1e40af", highlightthickness=2)
        password_frame.pack(fill="x", pady=(0, 30))
        self.login_password = tk.Entry(password_frame, font=("Segoe UI", 12), bg="#0f3460", 
                                      fg="white", show="●", relief="flat", insertbackground="white", bd=10)
        self.login_password.pack(fill="x")
        
        # Login button with hover effect
        login_btn = tk.Button(container, text="🚀 Login Now", font=("Segoe UI", 13, "bold"),
                             bg="#00d4ff", fg="#0a0a1e", width=20, height=2,
                             command=self._on_login, cursor="hand2", relief="flat",
                             activebackground="#00b4d8", activeforeground="#0a0a1e")
        login_btn.pack(pady=10)
        
        # Hover effects
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg="#0096c7"))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg="#00d4ff"))
        
        # Bind Enter key
        self.login_password.bind("<Return>", lambda e: self._on_login())
        self.login_username.bind("<Return>", lambda e: self.login_password.focus())
        
    def _build_register_tab(self, parent):
        """Build registration form"""
        container = tk.Frame(parent, bg="#16213e")
        container.pack(expand=True, padx=40, pady=15)
        
        # Header
        tk.Label(container, text="Create Account", 
                font=("Segoe UI", 20, "bold"), fg="#00d4ff", bg="#16213e").pack(pady=(0, 15))
        
        # Username
        tk.Label(container, text="👤 Username", 
                font=("Segoe UI", 10, "bold"), fg="#cbd5e1", bg="#16213e").pack(anchor="w", pady=(0, 5))
        username_frame = tk.Frame(container, bg="#0f3460", highlightbackground="#1e40af", highlightthickness=2)
        username_frame.pack(fill="x", pady=(0, 10))
        self.reg_username = tk.Entry(username_frame, font=("Segoe UI", 11), bg="#0f3460", 
                                    fg="white", relief="flat", insertbackground="white", bd=8)
        self.reg_username.pack(fill="x")
        
        # Full Name
        tk.Label(container, text="👨 Full Name", 
                font=("Segoe UI", 10, "bold"), fg="#cbd5e1", bg="#16213e").pack(anchor="w", pady=(0, 5))
        fullname_frame = tk.Frame(container, bg="#0f3460", highlightbackground="#1e40af", highlightthickness=2)
        fullname_frame.pack(fill="x", pady=(0, 10))
        self.reg_fullname = tk.Entry(fullname_frame, font=("Segoe UI", 11), bg="#0f3460", 
                                    fg="white", relief="flat", insertbackground="white", bd=8)
        self.reg_fullname.pack(fill="x")
        
        # Password
        tk.Label(container, text="🔒 Password", 
                font=("Segoe UI", 10, "bold"), fg="#cbd5e1", bg="#16213e").pack(anchor="w", pady=(0, 5))
        password_frame = tk.Frame(container, bg="#0f3460", highlightbackground="#1e40af", highlightthickness=2)
        password_frame.pack(fill="x", pady=(0, 10))
        self.reg_password = tk.Entry(password_frame, font=("Segoe UI", 11), bg="#0f3460", 
                                    fg="white", show="●", relief="flat", insertbackground="white", bd=8)
        self.reg_password.pack(fill="x")
        
        # Confirm Password
        tk.Label(container, text="🔒 Confirm Password", 
                font=("Segoe UI", 10, "bold"), fg="#cbd5e1", bg="#16213e").pack(anchor="w", pady=(0, 5))
        confirm_frame = tk.Frame(container, bg="#0f3460", highlightbackground="#1e40af", highlightthickness=2)
        confirm_frame.pack(fill="x", pady=(0, 15))
        self.reg_confirm = tk.Entry(confirm_frame, font=("Segoe UI", 11), bg="#0f3460", 
                                   fg="white", show="●", relief="flat", insertbackground="white", bd=8)
        self.reg_confirm.pack(fill="x")
        
        # Register button
        register_btn = tk.Button(container, text="✨ Create Account", font=("Segoe UI", 13, "bold"),
                                bg="#10b981", fg="white", width=20, height=2,
                                command=self._on_register, cursor="hand2", relief="flat",
                                activebackground="#059669", activeforeground="white")
        register_btn.pack(pady=10)
        
        # Hover effects
        register_btn.bind("<Enter>", lambda e: register_btn.config(bg="#059669"))
        register_btn.bind("<Leave>", lambda e: register_btn.config(bg="#10b981"))
        
        # Bind Enter key
        self.reg_confirm.bind("<Return>", lambda e: self._on_register())
    
    def _on_login(self):
        """Handle login button click"""
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        success, message = self.auth_manager.authenticate(username, password)
        
        if success:
            self.authenticated = True
            self.user_data = self.auth_manager.get_current_user()
            messagebox.showinfo("✅ Success", f"Welcome back, {self.user_data['full_name']}!")
            self.destroy()
        else:
            messagebox.showerror("❌ Login Failed", message)
            self.login_password.delete(0, "end")
    
    def _on_register(self):
        """Handle registration button click"""
        username = self.reg_username.get().strip()
        fullname = self.reg_fullname.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        
        # Validate password match
        if password != confirm:
            messagebox.showerror("❌ Error", "Passwords do not match")
            return
        
        success, message = self.auth_manager.register_user(username, password, fullname)
        
        if success:
            messagebox.showinfo("✅ Success", "Registration successful! You can now login.")
            # Switch to login tab
            self.notebook.select(0)
            # Clear registration fields
            self.reg_username.delete(0, "end")
            self.reg_fullname.delete(0, "end")
            self.reg_password.delete(0, "end")
            self.reg_confirm.delete(0, "end")
            # Set login username
            self.login_username.insert(0, username)
        else:
            messagebox.showerror("❌ Registration Failed", message)

# -----------------------------
# Domain Models
# -----------------------------

@dataclass
class Expense:
    id: int
    date: dt.date
    category: str
    description: str
    amount: float

    def to_row(self) -> List[str]:
        return [str(self.id), self.date.isoformat(), self.category, self.description, f"{self.amount:.2f}"]

    @staticmethod
    def from_row(row: List[str]) -> "Expense":
        return Expense(
            id=int(row[0]),
            date=dt.date.fromisoformat(row[1]),
            category=row[2],
            description=row[3],
            amount=float(row[4]),
        )

# -----------------------------
# Multi-Section Storage Layer
# -----------------------------

class MultiFileStorage:
    SECTIONS = {
        "personal": {"filename": "personal_expenses", "emoji": "👤", "color": "#e74c3c", "label": "Personal"},
        "family": {"filename": "family_expenses", "emoji": "👨‍👩‍👧", "color": "#3498db", "label": "Family"},
        "business": {"filename": "business_expenses", "emoji": "💼", "color": "#2ecc71", "label": "Business"}
    }

    def __init__(self, username: str):
        self.username = username
        self.storages = {}
        self._init_all_files()

    def _init_all_files(self):
        for section_key, section_info in self.SECTIONS.items():
            filepath = self._get_user_filepath(section_info["filename"])
            if not os.path.exists(filepath):
                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["id", "date", "category", "description", "amount"])
    
    def _get_user_filepath(self, base_filename: str) -> str:
        """Generate user-specific file path"""
        return f"{base_filename}_{self.username}.csv"

    def get_storage(self, section: str) -> 'FileStorage':
        if section not in self.storages:
            filepath = self._get_user_filepath(self.SECTIONS[section]["filename"])
            self.storages[section] = FileStorage(filepath)
        return self.storages[section]

    def get_section_info(self, section: str):
        return self.SECTIONS.get(section, self.SECTIONS["personal"])

class FileStorage:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.headers = ["id", "date", "category", "description", "amount"]
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)

    def load_all(self) -> List[Expense]:
        expenses = []
        try:
            with open(self.filepath, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                for row in reader:
                    if len(row) == 5:
                        try:
                            expenses.append(Expense.from_row(row))
                        except Exception:
                            continue
        except FileNotFoundError:
            pass
        return expenses

    def save_all(self, expenses: List[Expense]) -> None:
        with open(self.filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)
            for exp in expenses:
                writer.writerow(exp.to_row())

# BulkImportManager functionality moved to SectionManager static methods

# -----------------------------
# Business Logic
# -----------------------------

class SectionManager:
    def __init__(self, storage: MultiFileStorage, section: str, username: str = None):
        self.storage = storage.get_storage(section)
        self.section_key = section
        self.section_info = storage.get_section_info(section)
        self.username = username
        self.expenses: List[Expense] = self.storage.load_all()
        self.next_id = self._compute_next_id()
        self.categories: set = set(exp.category for exp in self.expenses) or {
            "Food", "Transport", "Rent", "Utilities", "Entertainment", "Misc"
        }

    def _compute_next_id(self) -> int:
        return (max((e.id for e in self.expenses), default=0) + 1)

    def add_expense(self, date: dt.date, category: str, description: str, amount: float) -> Expense:
        exp = Expense(id=self.next_id, date=date, category=category, description=description, amount=amount)
        self.expenses.append(exp)
        self.categories.add(category)
        self.next_id += 1
        self.storage.save_all(self.expenses)
        return exp

    def bulk_add_expenses(self, expenses_data: List[Dict]) -> Tuple[int, int]:
        """Add multiple expenses and return (success_count, skipped_count)"""
        success_count = 0
        skipped_count = 0
        
        for expense_data in expenses_data:
            try:
                date = dt.date.fromisoformat(expense_data['date'])
                category = expense_data['category'].strip()
                description = expense_data['description'].strip()
                amount = float(expense_data['amount'])
                
                exp = Expense(id=self.next_id, date=date, category=category, 
                            description=description, amount=amount)
                self.expenses.append(exp)
                self.categories.add(category)
                self.next_id += 1
                success_count += 1
            except Exception:
                skipped_count += 1
                continue
        
        if success_count > 0:
            self.storage.save_all(self.expenses)
        
        return success_count, skipped_count
    
    @staticmethod
    def parse_csv_file(filepath: str) -> List[Dict]:
        """Parse CSV file and return list of expense dictionaries"""
        try:
            df = pd.read_csv(filepath)
            expenses = []
            
            for idx, row in df.iterrows():
                expense = {
                    'date': row.get('date', ''),
                    'category': row.get('category', row.get('Category', '')),
                    'description': row.get('item', row.get('Item', row.get('description', ''))),
                    'amount': float(row.get('cost', row.get('Cost', row.get('amount', 0))))
                }
                expenses.append(expense)
            return expenses
        except Exception as e:
            raise ValueError(f"CSV parsing error: {str(e)}")
    
    @staticmethod
    def validate_expenses(expenses: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """Validate expenses and return valid ones with errors"""
        valid_expenses = []
        errors = []
        
        for i, expense in enumerate(expenses, 1):
            try:
                # Validate date
                dt.date.fromisoformat(expense['date'])
                
                # Validate amount
                amount = float(expense['amount'])
                if amount <= 0:
                    errors.append(f"Row {i}: Amount must be positive")
                    continue
                
                # Validate required fields
                if not expense['category'].strip():
                    errors.append(f"Row {i}: Category cannot be empty")
                    continue
                if not expense['description'].strip():
                    errors.append(f"Row {i}: Item/Description cannot be empty")
                    continue
                
                valid_expenses.append(expense)
                
            except ValueError as e:
                errors.append(f"Row {i}: Invalid date format - {str(e)}")
            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")
        
        return valid_expenses, errors

    def update_expense(self, expense_id: int, date: dt.date, category: str, description: str, amount: float) -> bool:
        for i, e in enumerate(self.expenses):
            if e.id == expense_id:
                self.expenses[i] = Expense(id=expense_id, date=date, category=category, description=description, amount=amount)
                self.categories.add(category)
                self.storage.save_all(self.expenses)
                return True
        return False

    def delete_expense(self, expense_id: int) -> bool:
        before = len(self.expenses)
        self.expenses = [e for e in self.expenses if e.id != expense_id]
        after = len(self.expenses)
        if after < before:
            self.storage.save_all(self.expenses)
            return True
        return False

    def filter_by_month(self, year: int, month: int) -> List[Expense]:
        return [e for e in self.expenses if e.date.year == year and e.date.month == month]

    def get_all(self) -> List[Expense]:
        return list(self.expenses)

    def add_category(self, category: str) -> None:
        self.categories.add(category)

    def get_categories(self) -> List[str]:
        return sorted(self.categories)

class Analyzer:
    @staticmethod
    def monthly_summary(expenses: List[Expense]) -> Dict:
        total = sum(e.amount for e in expenses)
        by_category = defaultdict(float)
        for e in expenses:
            by_category[e.category] += e.amount
        days = len(set(e.date for e in expenses)) or 1
        avg_per_day = total / days
        top_category, top_amount = (None, 0.0)
        if by_category:
            top_category, top_amount = max(by_category.items(), key=lambda x: x[1])
        return {
            "total": total,
            "avg_per_day": avg_per_day,
            "top_category_amount": top_amount,
            "top_category": top_category or "N/A",
        }

    @staticmethod
    def category_breakdown(expenses: List[Expense]) -> Dict[str, float]:
        breakdown = defaultdict(float)
        for e in expenses:
            breakdown[e.category] += e.amount
        return dict(breakdown)

    @staticmethod
    def daily_trend(expenses: List[Expense]) -> List[Tuple[dt.date, float]]:
        by_day = defaultdict(float)
        for e in expenses:
            by_day[e.date] += e.amount
        return sorted(by_day.items(), key=lambda x: x[0])

# Bulk Import Window now integrated in Personal Analytics NAV Bar under Category Stats

# -----------------------------
# Analytics Windows (Unchanged)
# -----------------------------

class AnalyticsWindow(tk.Toplevel):
    def __init__(self, parent, manager: SectionManager, year: int, month: int, chart_type: str, section_info: Dict):
        super().__init__(parent)
        self.manager = manager
        self.year = year
        self.month = month
        self.chart_type = chart_type
        self.section_emoji = section_info["emoji"]
        self.section_color = section_info["color"]
        self.expenses = self.manager.filter_by_month(year, month)
        
        self.title(f"{self.section_emoji} {chart_type.replace('_', ' ').title()} - {year}-{month:02d}")
        # Make window fullscreen
        self.state('zoomed')
        self.configure(bg="#f0f4f8")
        
        self._build_header()
        self._build_chart()
        self._build_footer()

    def _build_header(self):
        # Compact header optimized to fit accurately
        header_frame = tk.Frame(self, bg=self.section_color, height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Single decorative top bar
        top_bar = tk.Frame(header_frame, bg="#0ea5e9", height=2)
        top_bar.pack(fill="x")
        
        # Header content with minimal spacing
        content_frame = tk.Frame(header_frame, bg=self.section_color)
        content_frame.pack(expand=True, fill="both", padx=30, pady=8)
        
        # Left side - Title with icon
        left_section = tk.Frame(content_frame, bg=self.section_color)
        left_section.pack(side="left", fill="y")
        
        # Icon with smaller size
        icon_container = tk.Frame(left_section, bg=self.section_color)
        icon_container.pack(side="left", padx=(0, 10))
        
        tk.Label(icon_container, text=f"{self.section_emoji}", 
                font=("Segoe UI", 24), fg="white", bg=self.section_color).pack()
        
        # Text section
        text_section = tk.Frame(left_section, bg=self.section_color)
        text_section.pack(side="left", fill="y")
        
        tk.Label(text_section, text=f"{self.chart_type.replace('_', ' ').title()}", 
                font=("Segoe UI", 16, "bold"), fg="white", bg=self.section_color).pack(anchor="w", pady=(1, 0))
        tk.Label(text_section, text=f"📅 {self.year}-{self.month:02d} Analysis | Daily Breakdown", 
                font=("Segoe UI", 9), fg="#e0f2fe", bg=self.section_color).pack(anchor="w")
        
        # Right side - Quick stats badge
        right_section = tk.Frame(content_frame, bg=self.section_color)
        right_section.pack(side="right", padx=10)
        
        # Compact stats badge
        stats_badge = tk.Frame(right_section, bg="#0f3460", relief="flat")
        stats_badge.pack(pady=1)
        
        badge_inner = tk.Frame(stats_badge, bg="#0f3460")
        badge_inner.pack(padx=10, pady=5)
        
        total = sum(e.amount for e in self.expenses)
        tk.Label(badge_inner, text="Total Expenses", 
                font=("Segoe UI", 7), fg="#94a3b8", bg="#0f3460").pack()
        tk.Label(badge_inner, text=f"₹{total:,.0f}", 
                font=("Segoe UI", 13, "bold"), fg="#00d4ff", bg="#0f3460").pack()
        tk.Label(badge_inner, text=f"{len(self.expenses)} Txns", 
                font=("Segoe UI", 6), fg="#cbd5e1", bg="#0f3460").pack()

    def _build_chart(self):
        # Main container optimized for fullscreen without scrollbars
        container = tk.Frame(self, bg="#f0f4f8")
        container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Modern card design with shadow effect
        shadow_layer = tk.Frame(container, bg="#cbd5e1")
        shadow_layer.pack(fill="both", expand=True, padx=2, pady=2)
        
        chart_card = tk.Frame(shadow_layer, bg="white", relief="flat", bd=0)
        chart_card.pack(fill="both", expand=True)
        
        # Top accent bar for card
        accent_bar = tk.Frame(chart_card, bg=self.section_color, height=4)
        accent_bar.pack(fill="x")
        
        # Chart frame with optimized padding for perfect fullscreen fit
        chart_frame = tk.Frame(chart_card, bg="white")
        chart_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Create figure optimized for fullscreen display without scrolling
        self.fig = Figure(figsize=(17, 8.5), facecolor="white", dpi=85)
        
        if self.chart_type == "pie_chart":
            self._create_pie_chart()
        elif self.chart_type == "bar_chart":
            self._create_bar_chart()
        elif self.chart_type == "trend_chart":
            self._create_trend_chart()
        elif self.chart_type == "category_stats":
            self._create_category_table()
        
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.draw()

    def _build_footer(self):
        # Modern footer optimized for fullscreen
        footer_frame = tk.Frame(self, bg="#1e293b", height=75)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        # Double-layer top border
        border1 = tk.Frame(footer_frame, bg="#0ea5e9", height=2)
        border1.pack(fill="x")
        border2 = tk.Frame(footer_frame, bg="#38bdf8", height=1)
        border2.pack(fill="x")
        
        # Footer content with optimized organization
        content = tk.Frame(footer_frame, bg="#1e293b")
        content.pack(expand=True, fill="both", padx=50, pady=10)
        
        total = sum(e.amount for e in self.expenses)
        days_recorded = len(set(e.date for e in self.expenses))
        avg_per_day = total / days_recorded if days_recorded > 0 else 0
        
        # Create compact stat cards
        stats = [
            ("💰", "Total Spent", f"₹{total:,.2f}", "#00d4ff"),
            ("📅", "Transactions", str(len(self.expenses)), "#10b981"),
            ("📊", "Days Recorded", str(days_recorded), "#f59e0b"),
            ("📈", "Avg per Day", f"₹{avg_per_day:,.2f}", "#8b5cf6")
        ]
        
        for icon, label, value, color in stats:
            stat_card = tk.Frame(content, bg="#0f3460", relief="flat")
            stat_card.pack(side="left", padx=12, fill="y", expand=True)
            
            card_content = tk.Frame(stat_card, bg="#0f3460")
            card_content.pack(padx=15, pady=8)
            
            # Icon
            tk.Label(card_content, text=icon, font=("Segoe UI", 16), 
                    fg=color, bg="#0f3460").pack(side="left", padx=(0, 8))
            
            # Text section
            text_section = tk.Frame(card_content, bg="#0f3460")
            text_section.pack(side="left")
            
            tk.Label(text_section, text=label, font=("Segoe UI", 8), 
                    fg="#94a3b8", bg="#0f3460").pack(anchor="w")
            tk.Label(text_section, text=value, font=("Segoe UI", 13, "bold"), 
                    fg=color, bg="#0f3460").pack(anchor="w")

    def _create_pie_chart(self):
        breakdown = Analyzer.category_breakdown(self.expenses)
        self.ax = self.fig.add_subplot(111)
        if breakdown:
            labels = list(breakdown.keys())
            sizes = list(breakdown.values())
            # Professional gradient color palette
            colors = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', 
                     '#ec4899', '#06b6d4', '#14b8a6', '#f97316', '#6366f1',
                     '#84cc16', '#f43f5e', '#06b6d4', '#a855f7', '#eab308']
            colors = colors[:len(labels)]
            
            # Create pie chart with enhanced visual effects
            wedges, texts, autotexts = self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                                  startangle=90, colors=colors, 
                                                  textprops={'fontsize': 14, 'fontweight': 'bold'},
                                                  explode=[0.08]*len(labels),
                                                  shadow=True,
                                                  wedgeprops={'edgecolor': 'white', 'linewidth': 3, 'antialiased': True})            
  
            
            # Adjust subplot position
            self.fig.subplots_adjust(top=0.90, bottom=0.05, left=0.05, right=0.95)
        else:
            self.ax.text(0.5, 0.5, 'No data\nfor this month', ha='center', va='center', 
                        fontsize=32, fontweight='bold', color='#94a3b8')
            self.ax.set_title('Expense Category Breakdown', fontsize=26, fontweight='bold', 
                            pad=45, color='#1e293b',
                            bbox=dict(boxstyle='round,pad=0.8', facecolor='#f0f4f8', edgecolor='none'))
            self.fig.subplots_adjust(top=0.90, bottom=0.05, left=0.05, right=0.95)

    def _create_bar_chart(self):
        breakdown = Analyzer.category_breakdown(self.expenses)
        self.ax = self.fig.add_subplot(111)
        if breakdown:
            categories = list(breakdown.keys())
            amounts = list(breakdown.values())
            # Professional gradient colors
            colors = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', 
                     '#ec4899', '#06b6d4', '#14b8a6', '#f97316', '#6366f1',
                     '#84cc16', '#f43f5e', '#06b6d4', '#a855f7', '#eab308']
            colors = colors[:len(categories)]
            
            # Create bars with gradient effect
            bars = self.ax.bar(categories, amounts, color=colors, edgecolor='#1e293b', 
                             linewidth=2.5, alpha=0.85, width=0.7)
            
            # Add gradient effect to bars
            for bar, color in zip(bars, colors):
                bar.set_linewidth(2.5)
                bar.set_edgecolor('#1e293b')
            
            self.ax.set_title('Spending by Category', fontsize=22, fontweight='bold', 
                            pad=35, color='#1e293b',
                            bbox=dict(boxstyle='round,pad=0.6', facecolor='#f0f4f8', edgecolor='none'))
            self.ax.set_ylabel('Amount (₹)', fontsize=16, fontweight='bold', color='#1e293b', labelpad=12)
            self.ax.set_xlabel('Categories', fontsize=16, fontweight='bold', color='#1e293b', labelpad=12)
            plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=12, fontweight='bold')
            self.ax.tick_params(axis='y', labelsize=12)
            self.ax.grid(axis='y', alpha=0.25, linestyle='--', linewidth=1.5, color='#cbd5e1')
            self.ax.set_axisbelow(True)
            
            # Add professional value labels with background
            for bar, amount in zip(bars, amounts):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height + max(amounts)*0.02,
                           f'₹{amount:,.0f}', ha='center', va='bottom', 
                           fontweight='bold', fontsize=12, color='#1e293b',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='#fef08a', alpha=0.8, edgecolor='none'))
            
            # Adjust layout for perfect fit
            self.fig.subplots_adjust(top=0.88, bottom=0.16, left=0.10, right=0.95)
        else:
            self.ax.text(0.5, 0.5, 'No data\nfor this month', ha='center', va='center', 
                        fontsize=32, fontweight='bold', color='#94a3b8')
            self.ax.set_title('Spending by Category', fontsize=26, fontweight='bold', 
                            pad=45, color='#1e293b',
                            bbox=dict(boxstyle='round,pad=0.8', facecolor='#f0f4f8', edgecolor='none'))
            self.fig.subplots_adjust(top=0.90, bottom=0.05, left=0.05, right=0.95)

    def _create_trend_chart(self):
        import matplotlib.dates as mdates
        trend = Analyzer.daily_trend(self.expenses)
        self.ax = self.fig.add_subplot(111)
        if trend:
            dates = [t[0] for t in trend]
            amounts = [t[1] for t in trend]
            
            # Create professional gradient line chart
            self.ax.plot(dates, amounts, 'o-', linewidth=4, markersize=14, color='#0ea5e9', 
                        markerfacecolor='#0ea5e9', markeredgecolor='white', markeredgewidth=4,
                        label='Daily Spending', zorder=3, alpha=0.9)
            
            # Add enhanced gradient fill
            self.ax.fill_between(dates, amounts, alpha=0.25, color='#0ea5e9')
            
            # Add professional average line
            avg_amount = sum(amounts) / len(amounts)
            self.ax.axhline(y=avg_amount, color='#10b981', linestyle='--', linewidth=3, 
                          label=f'Average: ₹{avg_amount:,.2f}', alpha=0.8, zorder=2)
            
            # Enhanced styling
            self.ax.set_title('Daily Spending Trend Analysis', fontsize=22, fontweight='bold', 
                            pad=35, color='#1e293b',
                            bbox=dict(boxstyle='round,pad=0.6', facecolor='#f0f4f8', edgecolor='none'))
            self.ax.set_xlabel('Date', fontsize=16, fontweight='bold', color='#1e293b', labelpad=12)
            self.ax.set_ylabel('Amount (₹)', fontsize=16, fontweight='bold', color='#1e293b', labelpad=12)
            self.ax.grid(True, alpha=0.2, linestyle='--', linewidth=1.5, color='#cbd5e1')
            self.ax.set_axisbelow(True)
            
            # Professional date formatting
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
            self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
            plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=12, fontweight='bold')
            self.ax.tick_params(axis='y', labelsize=12)
            
            self.ax.legend(fontsize=12, loc='upper right', framealpha=0.95, shadow=True,
                         fancybox=True, borderpad=1)
            
            # Enhanced data point labels
            max_amount = max(amounts)
            min_amount = min(amounts)
            for date, amount in zip(dates, amounts):
                if amount == max_amount or amount == min_amount:
                    self.ax.annotate(f'₹{amount:,.0f}', 
                                   xy=(date, amount), 
                                   xytext=(0, 18 if amount == max_amount else -28),
                                   textcoords='offset points',
                                   ha='center',
                                   fontsize=11,
                                   fontweight='bold',
                                   color='#1e293b',
                                   bbox=dict(boxstyle='round,pad=0.4', facecolor='#fef08a', 
                                           alpha=0.95, edgecolor='#1e293b', linewidth=1.5))
            
            # Format y-axis
            self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
            
            # Adjust layout for perfect fit
            self.fig.subplots_adjust(top=0.88, bottom=0.16, left=0.10, right=0.95)
        else:
            self.ax.text(0.5, 0.5, 'No data\nfor this month', ha='center', va='center', 
                        fontsize=28, fontweight='bold', color='#94a3b8')
            self.ax.set_title('Daily Spending Trend Analysis', fontsize=22, fontweight='bold', 
                            pad=35, color='#1e293b',
                            bbox=dict(boxstyle='round,pad=0.6', facecolor='#f0f4f8', edgecolor='none'))
            self.fig.subplots_adjust(top=0.88, bottom=0.05, left=0.05, right=0.95)

    def _create_category_table(self):
        breakdown = Analyzer.category_breakdown(self.expenses)
        summary = Analyzer.monthly_summary(self.expenses)
        
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')
        table_data = [["Category", "Amount", "Percentage", "Transactions"]]
        
        if breakdown:
            total = summary['total']
            # Count transactions per category
            category_count = defaultdict(int)
            for e in self.expenses:
                category_count[e.category] += 1
            
            for cat, amt in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
                pct = (amt/total*100) if total > 0 else 0
                count = category_count[cat]
                table_data.append([cat, f"₹{amt:,.2f}", f"{pct:.1f}%", str(count)])
        else:
            table_data.append(["No data", "", "", ""])
        
        # Create professional table
        table = self.ax.table(cellText=table_data, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(14)
        table.scale(1.3, 3)
        
        # Professional color scheme
        colors = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', 
                 '#ec4899', '#06b6d4', '#14b8a6', '#f97316', '#6366f1']
        
        for i in range(len(table_data)):
            for j in range(4):
                cell = table[(i, j)]
                if i == 0:
                    # Enhanced header
                    cell.set_facecolor('#1e293b')
                    cell.set_text_props(weight='bold', color='white', fontsize=15)
                    cell.set_height(0.08)
                    cell.set_linewidth(1.5)
                    cell.set_edgecolor('#0ea5e9')
                else:
                    # Enhanced data cells
                    if i % 2 == 0:
                        cell.set_facecolor('#f8fafc')
                    else:
                        cell.set_facecolor('#ffffff')
                    cell.set_text_props(fontsize=13, weight='bold')
                    cell.set_linewidth(1)
                    cell.set_edgecolor('#e2e8f0')
                    
                    # Add color indicator to first column
                    if j == 0 and i > 0:
                        color_idx = (i - 1) % len(colors)
                        cell.set_facecolor(colors[color_idx])
                        cell.set_text_props(color='white', weight='bold', fontsize=13)
        
        self.ax.set_title('Category Spending Analysis', fontsize=22, fontweight='bold', 
                        pad=35, color='#1e293b',
                        bbox=dict(boxstyle='round,pad=0.6', facecolor='#f0f4f8', edgecolor='none'))
        
        # Adjust layout for perfect fit
        self.fig.subplots_adjust(top=0.88, bottom=0.05, left=0.05, right=0.95)

# -----------------------------
# Main GUI Layer with Sections + NEW IMPORT BUTTON
# -----------------------------

class ExpenseApp(tk.Tk):
    def __init__(self, user_data: Dict):
        super().__init__()
        # Hide window initially to prevent flashing
        self.withdraw()
        
        self.user_data = user_data
        self.auth_manager = AuthManager()
        self.username = user_data['username']
        
        self.title(f"💰 Expense Manager - Welcome {user_data['full_name']} 👋")
        self.geometry("1800x1000")
        self.configure(bg="#f0f4f8")
        
        self.multi_storage = MultiFileStorage(self.username)
        self.current_section = "personal"
        self.current_manager: Optional[SectionManager] = None
        self.current_year = dt.date.today().year
        self.current_month = dt.date.today().month
        self.selected_expense_id: Optional[int] = None

        # Modern navigation bar colors
        self.nav_bg = "#1e293b"
        self.nav_hover = "#334155"
        self.nav_active = "#0ea5e9"

        self._switch_section("personal")
        self._build_ui()
        self._refresh_all()
        
        # Show window after everything is built
        self.deiconify()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _on_close(self):
        """Handle application close"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.auth_manager.logout()
            self.destroy()

    def _switch_section(self, section: str):
        self.current_section = section
        self.current_manager = SectionManager(self.multi_storage, section, self.username)
        self.section_info = self.multi_storage.get_section_info(section)

    def _build_ui(self):
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # SECTION TABS (Updated with Import button)
        self._build_section_tabs(main_container)

        # Navigation Bar (Left Sidebar)
        self._build_navigation(main_container)

        # Main content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(side="right", fill="both", expand=True)

        # Top controls
        self._build_top_controls(content_frame)

        # Left panel - Form + Table
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._build_form(left_panel)
        self._build_table(left_panel)

        # Right panel - Summary
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side="right", fill="y", padx=(10, 0))

        self._build_summary(right_panel)

    def _build_section_tabs(self, parent):
        # Modern section selector with gradient
        section_frame = tk.Frame(parent, bg="#1e293b", height=80)
        section_frame.pack(fill="x")
        section_frame.pack_propagate(False)

        # User info on left with avatar-like styling
        user_container = tk.Frame(section_frame, bg="#1e293b")
        user_container.pack(side="left", padx=25, pady=15)
        
        tk.Label(user_container, text=f"👤 {self.user_data['full_name']}", 
                font=("Segoe UI", 12, "bold"), fg="#e0f2fe", bg="#1e293b").pack()
        tk.Label(user_container, text=f"@{self.user_data['username']}", 
                font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b").pack()
        
        # Logout button with modern styling
        logout_btn = tk.Button(section_frame, text="🚪 Logout", 
                             font=("Segoe UI", 11, "bold"), bg="#ef4444", fg="white",
                             command=self._on_logout, cursor="hand2", relief="flat",
                             activebackground="#dc2626", activeforeground="white",
                             padx=20, pady=8)
        logout_btn.pack(side="right", padx=20, pady=20)
        
        # Hover effect for logout button
        logout_btn.bind("<Enter>", lambda e: logout_btn.config(bg="#dc2626"))
        logout_btn.bind("<Leave>", lambda e: logout_btn.config(bg="#ef4444"))

        self.section_var = tk.StringVar(value="personal")
        self.section_buttons = {}

        # Section buttons container
        buttons_container = tk.Frame(section_frame, bg="#1e293b")
        buttons_container.pack(side="left", fill="both", expand=True, padx=25)

        for section_key, info in MultiFileStorage.SECTIONS.items():
            btn = tk.Button(buttons_container, 
                           text=f"{info['emoji']} {info['label']}", 
                           font=("Segoe UI", 13, "bold"),
                           bg=info['color'], fg="white", relief="flat", height=2,
                           activebackground="#0ea5e9", activeforeground="white",
                           command=lambda s=section_key: self._on_section_switch(s),
                           cursor="hand2", padx=15)
            btn.pack(side="left", fill="both", expand=True, padx=3)
            
            # Enhanced hover effects with shadow simulation
            def on_enter(e, b=btn, c=info['color']):
                b.config(bg="#0ea5e9", font=("Segoe UI", 13, "bold"))
            def on_leave(e, b=btn, c=info['color']):
                b.config(bg=c, font=("Segoe UI", 13, "bold"))
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            self.section_buttons[section_key] = btn
    
    def _on_logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.auth_manager.logout()
            self.destroy()
            # Restart application
            main()

    def _on_section_switch(self, section: str):
        self._switch_section(section)
        self.section_var.set(section)
        
        # Update button states
        for sec, btn in self.section_buttons.items():
            btn.config(bg=MultiFileStorage.SECTIONS[sec]['color'])
        self.section_buttons[section].config(bg=self.section_info['color'])
        
        self._refresh_all()
        self.section_buttons[section].config(relief="raised")

    def _build_navigation(self, parent):
        nav_frame = tk.Frame(parent, bg=self.nav_bg, width=270)
        nav_frame.pack(side="left", fill="y")
        nav_frame.pack_propagate(False)

        # Modern header with icon
        header_container = tk.Frame(nav_frame, bg=self.nav_bg)
        header_container.pack(pady=25, padx=20, fill="x")
        
        tk.Label(header_container, text=f"{self.section_info['emoji']}", 
                font=("Segoe UI", 36), fg="#0ea5e9", bg=self.nav_bg).pack()
        tk.Label(header_container, text="Analytics Dashboard", 
                font=("Segoe UI", 12, "bold"), fg="#e0f2fe", bg=self.nav_bg).pack(pady=(10, 0))

        # Divider
        tk.Frame(nav_frame, bg="#334155", height=2).pack(fill="x", padx=20, pady=15)

        nav_buttons = [
            ("🥧 Pie Chart", "pie_chart"),
            ("📊 Bar Chart", "bar_chart"),
            ("📈 Trend Analysis", "trend_chart"),
            ("📋 Category Stats", "category_stats"),
            ("📥 Bulk Import", "bulk_import")
        ]

        self.nav_buttons = {}
        for text, chart_type in nav_buttons:
            btn = tk.Button(nav_frame, text=text, font=("Segoe UI", 11, "bold"), 
                           bg=self.nav_bg, fg="#cbd5e1", relief="flat", height=2,
                           activebackground=self.nav_active, activeforeground="white",
                           command=lambda t=chart_type: self._on_nav_button_click(t),
                           cursor="hand2", anchor="w", padx=20)
            btn.pack(fill="x", padx=15, pady=5)
            
            # Enhanced hover effect
            def on_enter(e, b=btn):
                b.config(bg=self.nav_hover, fg="white")
            def on_leave(e, b=btn):
                b.config(bg=self.nav_bg, fg="#cbd5e1")
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            self.nav_buttons[chart_type] = btn
        
        # Footer info in navigation
        tk.Frame(nav_frame, bg="#334155", height=1).pack(fill="x", padx=20, pady=20, side="bottom")
        footer_info = tk.Label(nav_frame, text=f"📅 {dt.date.today().strftime('%B %Y')}", 
                              font=("Segoe UI", 10), fg="#64748b", bg=self.nav_bg)
        footer_info.pack(side="bottom", pady=10)
    
    def _on_nav_button_click(self, chart_type: str):
        """Handle navigation button clicks"""
        if chart_type == "bulk_import":
            self._open_bulk_import_window()
        else:
            self._open_analytics_window(chart_type)

    def _open_analytics_window(self, chart_type: str):
        if self.current_manager:
            window = AnalyticsWindow(self, self.current_manager, self.current_year, self.current_month, 
                                   chart_type, self.section_info)
            window.transient(self)
            window.grab_set()
    
    def _open_bulk_import_window(self):
        """Open bulk import window integrated under Category Stats"""
        window = tk.Toplevel(self)
        window.title("📥 Bulk Import Expenses")
        window.geometry("1200x700")
        window.configure(bg="#f8f9fa")
        
        import_data = []
        valid_data = []
        errors = []
        
        # Header
        header = tk.Label(window, text="📥 Bulk Import Expenses", font=("Arial", 20, "bold"), 
                         bg="#2ecc71", fg="white")
        header.pack(fill="x", pady=10)
        
        # Main container
        main_frame = ttk.Frame(window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="📁 Select File", padding=15)
        file_frame.pack(fill="x", pady=(0, 10))
        
        file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=file_var, width=50).pack(side="left", padx=(0, 10))
        
        # Section selection
        section_frame = ttk.LabelFrame(main_frame, text="📂 Target Section", padding=15)
        section_frame.pack(fill="x", pady=(0, 10))
        
        section_var = tk.StringVar(value="personal")
        sections = ["personal", "family", "business"]
        for i, section in enumerate(sections):
            rb = ttk.Radiobutton(section_frame, text=f"{MultiFileStorage.SECTIONS[section]['emoji']} {MultiFileStorage.SECTIONS[section]['label']}", 
                               variable=section_var, value=section)
            rb.pack(anchor="w")
        
        # Preview table
        table_frame = ttk.LabelFrame(main_frame, text="👀 Data Preview (First 50 rows)", padding=10)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        columns = ("date", "category", "item", "cost")
        preview_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        for col in columns:
            preview_tree.heading(col, text=col.title())
            preview_tree.column(col, width=150)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=preview_tree.yview)
        preview_tree.configure(yscroll=vsb.set)
        preview_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        # Status and buttons
        status_frame = tk.Frame(window)
        status_frame.pack(fill="x", pady=10)
        
        status_label = tk.Label(status_frame, text="No file selected", fg="gray")
        status_label.pack(side="left")
        
        def browse_file():
            filepath = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )
            if filepath:
                file_var.set(filepath)
                load_preview(filepath)
        
        def load_preview(filepath):
            nonlocal import_data
            try:
                import_data = SectionManager.parse_csv_file(filepath)
                status_label.config(text=f"Loaded {len(import_data)} rows", fg="green")
                
                # Show first 50 rows
                for item in preview_tree.get_children():
                    preview_tree.delete(item)
                
                for expense in import_data[:50]:
                    preview_tree.insert("", "end", values=(
                        expense['date'], 
                        expense['category'][:20], 
                        expense['description'][:25], 
                        f"₹{expense['amount']:.2f}"
                    ))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
        
        def validate_data():
            nonlocal valid_data, errors
            if not import_data:
                messagebox.showwarning("No Data", "Please select a CSV file first.")
                return
            
            valid_data, errors = SectionManager.validate_expenses(import_data)
            
            error_text = f"✅ {len(valid_data)} valid / ❌ {len(errors)} errors"
            status_label.config(text=error_text, fg="blue")
            
            if errors:
                error_window = tk.Toplevel(window)
                error_window.title("Validation Errors")
                error_window.geometry("600x400")
                
                text = tk.Text(error_window, wrap="word")
                text.pack(fill="both", expand=True, padx=10, pady=10)
                text.insert("end", "\n".join(errors[:50]))
        
        def import_data_final():
            if not valid_data:
                messagebox.showwarning("No Valid Data", "No valid data to import.")
                return
            
            section = section_var.get()
            manager = SectionManager(self.multi_storage, section, self.username)
            
            success_count, skipped_count = manager.bulk_add_expenses(valid_data)
            
            message = f"✅ Imported {success_count} expenses to {MultiFileStorage.SECTIONS[section]['emoji']} {MultiFileStorage.SECTIONS[section]['label']} section!\n"
            if skipped_count > 0:
                message += f"⚠️ Skipped {skipped_count} invalid rows"
            
            messagebox.showinfo("Import Complete", message)
            self._switch_section(section)
            self._refresh_all()
            window.destroy()
        
        btn_frame = tk.Frame(status_frame)
        btn_frame.pack(side="right")
        
        ttk.Button(file_frame, text="Browse CSV", command=browse_file).pack(side="left")
        ttk.Button(btn_frame, text="🔍 Validate", command=validate_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✅ Import All", command=import_data_final).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=window.destroy).pack(side="left", padx=5)

    def _build_top_controls(self, parent):
        frame = ttk.LabelFrame(parent, text=f"🔍 Filters & Export - {self.section_info['emoji']} {self.section_info['label']}", padding=10)
        frame.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Year:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.year_var = tk.StringVar(value=str(self.current_year))
        ttk.Entry(frame, textvariable=self.year_var, width=8).grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Month:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.month_var = tk.StringVar(value=str(self.current_month))
        ttk.Entry(frame, textvariable=self.month_var, width=5).grid(row=0, column=3, padx=5)

        ttk.Button(frame, text="🔎 Filter", command=self._on_filter).grid(row=0, column=4, padx=5)
        ttk.Button(frame, text="🔄 Reset", command=self._on_reset_filter).grid(row=0, column=5, padx=5)
        ttk.Button(frame, text="📤 Export CSV", command=self._on_export).grid(row=0, column=6, padx=5)

    # ... [Rest of the methods remain exactly the same as original code] ...

    def _build_form(self, parent):
        frame = ttk.LabelFrame(parent, text="➕ Add / Edit Expense", padding=10)
        frame.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="📅 Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.date_var = tk.StringVar(value=dt.date.today().isoformat())
        ttk.Entry(frame, textvariable=self.date_var, width=15).grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="🏷️ Category:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(frame, textvariable=self.category_var, width=18)
        self.category_combo.grid(row=0, column=3, padx=5)
        ttk.Button(frame, text="+ Category", command=self._on_add_category).grid(row=0, column=4, padx=5)

        ttk.Label(frame, text="📝 Description:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.desc_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.desc_var, width=35).grid(row=1, column=1, columnspan=3, padx=5, sticky="ew")

        ttk.Label(frame, text="💰 Amount (₹):").grid(row=1, column=4, sticky="w", padx=(0, 5))
        self.amount_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.amount_var, width=12).grid(row=1, column=5, padx=5)

        ttk.Button(frame, text="✅ Add", command=self._on_add).grid(row=2, column=0, padx=5, pady=10)
        ttk.Button(frame, text="✏️ Update", command=self._on_update).grid(row=2, column=1, padx=5, pady=10)
        ttk.Button(frame, text="🗑️ Delete", command=self._on_delete).grid(row=2, column=2, padx=5, pady=10)
        ttk.Button(frame, text="🔄 Clear", command=self._clear_form).grid(row=2, column=3, padx=5, pady=10)

        for i in range(6):
            frame.grid_columnconfigure(i, weight=1)

    def _build_table(self, parent):
        frame = ttk.LabelFrame(parent, text="📋 Expenses List", padding=5)
        frame.pack(fill="both", expand=True)

        columns = ("id", "date", "category", "description", "amount")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=80 if col == "id" else 120 if col != "description" else 450, anchor="center")
        
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        
        self.tree.bind("<<TreeviewSelect>>", self._on_select_row)

    def _build_summary(self, parent):
        self.summary_frame = ttk.LabelFrame(parent, text="📊 Monthly Summary", padding=15)
        self.summary_frame.pack(fill="both", expand=True)
        
        self.summary_text = tk.Text(self.summary_frame, height=28, wrap="word", font=("Consolas", 11))
        scrollbar = ttk.Scrollbar(self.summary_frame, orient="vertical", command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=scrollbar.set)
        
        self.summary_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _refresh_all(self):
        self._refresh_categories()
        self._refresh_table()
        self._refresh_summary()

    def _refresh_categories(self):
        if self.current_manager:
            self.category_combo['values'] = self.current_manager.get_categories()
            if self.current_manager.categories:
                self.category_combo.set(list(self.current_manager.categories)[0])

    # ---------- Event Handlers ----------

    def _on_filter(self):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            if not (1 <= month <= 12):
                raise ValueError("Month must be between 1 and 12.")
            self.current_year, self.current_month = year, month
            self._refresh_table()
            self._refresh_summary()
        except ValueError as e:
            messagebox.showerror("❌ Invalid Filter", str(e))

    def _on_reset_filter(self):
        today = dt.date.today()
        self.year_var.set(str(today.year))
        self.month_var.set(str(today.month))
        self.current_year, self.current_month = today.year, today.month
        self._refresh_table()
        self._refresh_summary()

    def _on_export(self):
        if not self.current_manager:
            return
        expenses = self.current_manager.filter_by_month(self.current_year, self.current_month)
        if not expenses:
            messagebox.showinfo("📤 Export", "No expenses for selected month.")
            return
        filename = f"{self.current_section}_{self.current_year}_{self.current_month:02d}_expenses.csv"
        path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                          filetypes=[("CSV files", "*.csv")],
                                          initialfilename=filename)
        if path:
            try:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["id", "date", "category", "description", "amount"])
                    for e in expenses:
                        writer.writerow(e.to_row())
                messagebox.showinfo("✅ Export Success", f"Exported {len(expenses)} records!")
            except Exception as e:
                messagebox.showerror("❌ Export Failed", str(e))

    def _on_add_category(self):
        def commit():
            name = entry.get().strip()
            if name and self.current_manager:
                self.current_manager.add_category(name)
                self._refresh_categories()
                dialog.destroy()

        dialog = tk.Toplevel(self)
        dialog.title("➕ Add Category")
        dialog.geometry("300x120")
        dialog.transient(self)
        dialog.grab_set()
        ttk.Label(dialog, text="Category name:").pack(padx=10, pady=5)
        entry = ttk.Entry(dialog, width=30)
        entry.pack(padx=10, pady=5)
        ttk.Button(dialog, text="Add", command=commit).pack(pady=10)
        entry.focus()

    def _on_add(self):
        if not self.current_manager:
            return
        payload = self._validate_form()
        if payload:
            date, category, desc, amount = payload
            exp = self.current_manager.add_expense(date, category, desc, amount)
            self._refresh_all()
            self._clear_form()
            messagebox.showinfo("✅ Added", f"{self.section_info['emoji']} Expense #{exp.id} added!")

    def _on_update(self):
        if not self.current_manager or self.selected_expense_id is None:
            messagebox.showerror("❌ Update Error", "Select an expense first.")
            return
        payload = self._validate_form()
        if payload:
            date, category, desc, amount = payload
            if self.current_manager.update_expense(self.selected_expense_id, date, category, desc, amount):
                self._refresh_all()
                self._clear_form()
                messagebox.showinfo("✅ Updated", f"{self.section_info['emoji']} Expense updated!")
            else:
                messagebox.showerror("❌ Update Failed", "Record not found.")

    def _on_delete(self):
        if not self.current_manager or self.selected_expense_id is None:
            messagebox.showerror("❌ Delete Error", "Select an expense first.")
            return
        if messagebox.askyesno("⚠️ Confirm Delete", f"Delete expense #{self.selected_expense_id}?"):
            if self.current_manager.delete_expense(self.selected_expense_id):
                self._refresh_all()
                self._clear_form()
                messagebox.showinfo("✅ Deleted", f"{self.section_info['emoji']} Expense deleted!")
            else:
                messagebox.showerror("❌ Delete Failed", "Record not found.")

    def _on_select_row(self, _event):
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0])["values"]
            self.selected_expense_id = int(values[0])
            self.date_var.set(values[1])
            self.category_var.set(values[2])
            self.desc_var.set(values[3])
            self.amount_var.set(str(values[4]))

    def _validate_form(self) -> Optional[Tuple[dt.date, str, str, float]]:
        try:
            date = dt.date.fromisoformat(self.date_var.get().strip())
        except ValueError:
            messagebox.showerror("❌ Invalid Date", "Use YYYY-MM-DD format.")
            return None
        
        category = self.category_var.get().strip()
        if not category:
            messagebox.showerror("❌ Empty Category", "Category cannot be empty.")
            return None
        
        desc = self.desc_var.get().strip()
        if not desc:
            messagebox.showerror("❌ Empty Description", "Description cannot be empty.")
            return None
        
        try:
            amount = float(self.amount_var.get().strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("❌ Invalid Amount", "Amount must be positive number.")
            return None
        
        return date, category, desc, amount

    def _clear_form(self):
        self.selected_expense_id = None
        self.date_var.set(dt.date.today().isoformat())
        self.category_combo.set("")
        self.desc_var.set("")
        self.amount_var.set("")

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if self.current_manager:
            expenses = self.current_manager.filter_by_month(self.current_year, self.current_month)
            for e in expenses:
                self.tree.insert("", "end", values=(e.id, e.date.isoformat(), e.category, e.description, f"{e.amount:.2f}"))

    def _refresh_summary(self):
        if not self.current_manager:
            return
        expenses = self.current_manager.filter_by_month(self.current_year, self.current_month)
        breakdown = Analyzer.category_breakdown(expenses)
        summary = Analyzer.monthly_summary(expenses)
        
        text = f"{self.section_info['emoji']} {self.section_info['label']} - MONTHLY ANALYSIS\n"
        text += f"{self.current_year}-{self.current_month:02d} | " + "=" * 60 + "\n\n"
        text += f"💰 Total Spent: ₹{summary['total']:,.2f}\n"
        text += f"📅 Days Recorded: {len(set(e.date for e in expenses))}\n"
        text += f"📈 Average/Day: ₹{summary['avg_per_day']:,.2f}\n\n"
        
        if breakdown:
            text += "🏷️  CATEGORY BREAKDOWN (Top 10):\n"
            text += "─" * 60 + "\n"
            for cat, amt in sorted(breakdown.items(), key=lambda x: x[1], reverse=True)[:10]:
                pct = (amt/summary['total']*100) if summary['total'] > 0 else 0
                text += f"{cat:<20} ₹{amt:>12,.2f} ({pct:>6.1f}%)\n"
        else:
            text += "No expenses recorded for this month.\n"
        
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("end", text)


# -----------------------------
# Entry Point
# -----------------------------

def main():
    # Show login window first
    login_window = LoginWindow()
    login_window.mainloop()
    
    # Check if authentication was successful
    if login_window.authenticated and login_window.user_data:
        # Launch main application with user data
        app = ExpenseApp(login_window.user_data)
        app.mainloop()
    else:
        print("Authentication failed or cancelled")


if __name__ == "__main__":
    main()
