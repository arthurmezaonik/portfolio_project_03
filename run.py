import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('coders_bistro')

class Customer:
    "Create a new customer"
    def __init__ (self, f_name, l_name, email):
        #instance attibutes
        self.f_name = f_name
        self.l_name = l_name
        self.email = email
    
    def info(self):
        return f'Thaks for visiting us {self.f_name} {self.l_name}. Your order was sent on {self.email} email.'

customer = Customer("Arthur", "Martins", "arthur.mezaonik@gmail.com")
print(customer.info())

def run():
    print("Welcome to the Coders Bistro.\n")
    print("Are you already registered?\n")