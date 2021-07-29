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
        self.balance = []

    def info(self):
        return f'Client: {self.f_name} {self.l_name}. Email: {self.email}. Balance: {self.balance}'

    def full_name(self):
        return f'{self.f_name} {self.l_name}'


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
    Check if the user is really registered.
    If not, register a new client.
    """
    customer_data = []

    if value.lower() == "y":
        print("Good to have you back!")
        print("I just need to check your email.")
        email = check_email()
        row = find_row(email)
        customer_data = get_customer_data(row)

    elif value.lower() == "n":
        print("First time here!")
        print("Let's make a register for you")
        print("I just need a few information")
        customer_data = collect_new_customer_data()
        update_worksheet(customer_data, "clients")

    return customer_data


def check_email():
    """
    Check if the email is already registered
    """
    client_sheet = SHEET.worksheet("clients")
    email_collum = client_sheet.col_values(3)

    while True:
        print("Can you write it for me?")
        email = input("Enter your answear here:\n")

        if validate_email(email):
            if email in email_collum:
                break
            else:
                print("Sorry, I can't find your email.")
                print("Can we try again?\n")

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


def get_customer_data(row):
    """
    From the worksheet data, generate a client
    """
    client_sheet = SHEET.worksheet("clients")
    customer_data = client_sheet.row_values(row)

    return [customer_data[0], customer_data[1], customer_data[2]]


def collect_new_customer_data():
    """
    Colect user data and check if its not already registered
    """
    client_sheet = SHEET.worksheet("clients")
    email_collum = client_sheet.col_values(3)

    f_name = input("What's your first name?\n")
    l_name = input("What's your last name?\n")

    while True:
        email = input("What's your email?\n")

        if email not in email_collum:
            if validate_email(email):
                break
        else:
            print("Sorry, this email is already in use")
            print("Can we try again?\n")

    return [f_name, l_name, email]


def update_worksheet(data, worksheet):
    """
    Receives a list of integers to be inserted into a worksheet
    Update the relevant worksheet with the data provided
    """
    print(f"Updating {worksheet} worksheet...\n")
    worksheet_to_update = SHEET.worksheet(worksheet)
    worksheet_to_update.append_row(data)
    print(f"{worksheet} worksheet updated successfully\n")


def create_customer(data):
    """
    Create the customer
    """
    return Customer(data[0], data[1], data[2])


def menu_options():
    """
    Present the menus and return user otpion
    """
    print("A - Foods menu")
    print("B - Drinks menu")
    print("C - Deserts menu")
    menu_option = input("Enter your answear here:\n").upper()

    while menu_option not in ("A", "B", "C"):
        print("Please choose between one of the options")
        menu_option = input("Enter your answear here:\n").upper()

    return menu_option


def display_menu(menu_option):
    """
    Print the menu on the screen
    """
    option = menu_option.upper()
    if option == "A":
        menu_sheet = SHEET.worksheet("food_menu").get_all_values()
    elif option == "B":
        menu_sheet = SHEET.worksheet("drink_menu").get_all_values()
    elif option == "C":
        menu_sheet = SHEET.worksheet("deserts_menu").get_all_values()

    for item in menu_sheet:
        print(f'{item[0]:_<15}{item[1]:_>15}')


def add_balance(customer, value):
    customer.balance.append(value)


def main():
    print("Welcome to the Coders Bistro\n")

    is_registred_answear = is_registred()
    customer_data = need_to_be_register(is_registred_answear)
    customer = create_customer(customer_data)

    print("All done. Wich menu do you want to check first?\n")
    menu_option = menu_options()
    display_menu(menu_option)

    add_balance(customer, 50)
    add_balance(customer, 150)
    add_balance(customer, 20)
    add_balance(customer, 7)
    print(customer.info())


main()
