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
        return f'Client: {self.f_name} {self.l_name}. Email: {self.email}'


def is_registred():
    """
    Check if the user is already registered
    """
    while True:
        print("Are you registered (Y / N)?")
        first_answear = input("Enter your answear here:\n")

        if validate_is_registred(first_answear):
            break

    return first_answear


def validate_is_registred(data):
    """
    Validate the answear for the is_registered question
    """
    try:
        answear = data.strip().lower()
        if answear not in ("y", "n"):
            raise ValueError('Choose between Y or N')

    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")
        return False

    return True


def need_to_be_register(value):
    """
    Based on the previous answear, check if the client need to be register
    """
    if value == "y":
        email = check_email()
        row = find_row(email)
        customer = create_customer(row)
        print(customer.info())
    elif value == "n":
        pass


def check_email():
    """
    Check if the email is already registered
    """
    client_sheet = SHEET.worksheet("clients")
    email_collum = client_sheet.col_values(3)

    while True:
        print("What is you email?")
        email = input("Enter your answear here:\n")

        if validate_email(email):
            if email in email_collum:
                print("Valid email")
                break
            else:
                print("Email not found.")
                print("Try again.\n")

    return email


def validate_email(email_to_validate):
    """
    Validate email address
    """
    try:
        if "@" not in email_to_validate:
            raise ValueError("Please enter a valid email")
    except ValueError as e:
        print(f"Invalid data: {e}")
        print("Example: code@codersbistro.com\n")
        return False

    return True


def find_row(email):
    """
    From the email, find user on the worksheet
    """
    client_sheet = SHEET.worksheet("clients")
    cell = client_sheet.find(email)

    return cell.row


def create_customer(row):
    client_sheet = SHEET.worksheet("clients")
    customer_data = client_sheet.row_values(row)

    return Customer(customer_data[0], customer_data[1], customer_data[2])


def main():
    print("Welcome to the Coders Bistro\n")

    is_registred_answear = is_registred()
    need_to_be_register(is_registred_answear)


main()
