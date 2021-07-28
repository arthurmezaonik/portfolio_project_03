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
    def __init__(self, f_name, l_name, email):
        # Instance attibutes
        self.f_name = f_name
        self.l_name = l_name
        self.email = email

    def info(self):
        return f'Thaks for visiting us {self.f_name} {self.l_name}. Your order was sent on {self.email}'


def is_registred():
    """
    Check if the user is already registered
    """
    while True:
        print("Are you registered (Y / N)?")
        first_answear = input("Enter your answear here:\n")

        if validate_is_registred(first_answear):
            print("Valid answear")
            break

    return first_answear


def validate_is_registred(data):
    """
    Validate the answear for the is_registered question
    """
    try:
        answear = data.strip().lower()
        if answear not in ("y", "n"):
            raise ValueError('Please choose between Y or N')

    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")
        return False

    return True
