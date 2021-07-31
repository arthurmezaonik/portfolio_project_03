import gspread
from google.oauth2.service_account import Credentials
from datetime import date
from time import sleep

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
    "Create a customer"
    def __init__(self, f_name, l_name, email):
        # Instance attibutes
        self.f_name = f_name
        self.l_name = l_name
        self.email = email
        self.balance = []

    def info(self):
        return f'Client: {self.f_name} {self.l_name}.Email: {self.email}.Balance: {self.balance}'

    def full_name(self):
        return f'{self.f_name} {self.l_name}'


class Admin:
    """
    Create a admin
    """
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def info(self):
        return f'Email: {self.email} Password: {self.password}'

    def check_sales(self, date):
        """
        Check the sum of the sales for the chosen day
        """
        worksheet = select_worksheet("sales")
        day_col = worksheet.col_values(1)
        sales = worksheet.get_all_values()
        total = 0

        if date not in day_col:
            print(f"Sorry, we don't have ane register for {date}")

            return False
        else:
            for sale in sales:
                if sale[0] == date:
                    num_sheet = sale[1]
                    num = num_sheet.replace(",", ".")
                    total += float(num)

            print(f"The sales' total on {date} is ${total}")

            return True

    def new_expanse(self):
        """
        Register a new expanse on the worksheet
        """
        today = date.today().strftime("%d-%m-%Y")
        print("How much is the expnase?")
        print("Example: 15.50")
        value = float(input("Enter your answear here:\n"))
        print("Give a small description for your expanse")
        description = input("Enter your answear here:\n")

        data = [today, value, description]
        update_worksheet(data, "expenses")


def is_registred():
    """
    Check if the user is already registered
    """
    while True:
        print("Are you registered (Y / N)?")
        first_answear = input("Enter your answear here:\n")
        print(" ")
        print("# "*15)
        print(" ")
        if validate_yes_no(first_answear):
            break

    return first_answear


def validate_yes_no(data):
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
        # Passed a 'random' str on the function to return clients list
        worksheet = select_worksheet("random")
        email = check_email(worksheet, 3)
        row = find_row(email, worksheet)
        customer_data = get_customer_data(row)

    elif value.lower() == "n":
        print("First time here!")
        print("Let's make a register for you")
        print("I just need a few information")
        customer_data = collect_new_customer_data()
        update_worksheet(customer_data, "clients")

    return customer_data


def check_email(sheet, col):
    """
    Check if the email is already registered
    """
    worksheet = sheet
    email_collum = worksheet.col_values(col)

    while True:
        print("Can you write it for me?")
        email = input("Enter your answear here:\n")
        print(" ")
        print("# "*15)
        print(" ")

        if validate_email(email):
            if email in email_collum:
                break
            else:
                print("Sorry, I can't find your email.")
                print("Let's try again.\n")

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


def find_row(item, sheet):
    """
    From the email, find user on the worksheet
    """
    client_sheet = sheet
    cell = client_sheet.find(item)

    return cell.row


def get_customer_data(row):
    """
    From the worksheet data, generate a client
    """

    # Passed a 'random' str on the function to return clients list
    client_sheet = select_worksheet("random")
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

    print(" ")
    print("# "*15)
    print(" ")

    return [f_name, l_name, email]


def update_worksheet(data, worksheet):
    """
    Receives a list of integers to be inserted into a worksheet
    Update the relevant worksheet with the data provided
    """
    print(f"Updating {worksheet} worksheet...\n")
    worksheet_to_update = SHEET.worksheet(worksheet)
    worksheet_to_update.append_row(data)
    print(f"{worksheet} worksheet updated successfully")
    print(" ")
    print("# "*15)
    print(" ")


def create_customer(data):
    """
    Create the customer
    """
    return Customer(data[0], data[1], data[2])


def menu_options():
    """
    Present the menus and return user otpion
    """
    print("Wich menu do you want to check?")
    print("A - Foods menu")
    print("B - Drinks menu")
    print("C - Deserts menu")
    menu_option = input("Enter your answear here:\n").upper()
    print(" ")
    print("# "*15)
    print(" ")

    while menu_option not in ("A", "B", "C"):
        print("Please choose between one of the options")
        menu_option = input("Enter your answear here:\n").upper()

    return menu_option


def display_menu(sheet):
    """
    Print the menu on the screen
    """
    menu_sheet = sheet.get_all_values()

    for item in menu_sheet:
        print(f'{item[0]:<5}{item[1]:_<20}{item[2]:_>20}')


def customer_order(worksheet):
    """
    Collect the user order
    """
    while True:
        print("What's the ID from the item that you want?")
        id = input("Enter your answear here:\n")
        print(" ")
        print("# "*15)
        print(" ")

        if validate_customer_order(id, worksheet):
            print("Noted!")
            break

    return id


def validate_customer_order(id, worksheet):
    """
    Validate the ID passed from the user
    """
    ids = worksheet.col_values(1)
    try:
        if id not in ids:
            raise ValueError("Choose between one of the printed Ids")
    except ValueError as e:
        print(f"Invalid option: {e}, please try again.\n")
        return False

    return True


def select_worksheet(option):
    worksheet = ""

    if option.upper() == "A":
        worksheet = SHEET.worksheet("food_menu")
    elif option.upper() == "B":
        worksheet = SHEET.worksheet("drink_menu")
    elif option.upper() == "C":
        worksheet = SHEET.worksheet("deserts_menu")
    elif option.upper() == "ADMIN":
        worksheet = SHEET.worksheet("admin")
    elif option.upper() == "SALES":
        worksheet = SHEET.worksheet("sales")
    elif option.upper() == "EXPANSES":
        worksheet = SHEET.worksheet("expanses")
    else:
        worksheet = SHEET.worksheet("clients")

    return worksheet


def get_value(id, sheet):
    row = find_row(id, sheet)
    item_row = sheet.row_values(row)

    return item_row[2]


def add_balance(customer, value):
    """
    Add value on the customer balance
    """
    customer.balance.append(float(value))


def ordering():
    """
    Check if the user wants to keep ordering
    """
    while True:
        answear = input("Enter your answear here:\n")
        print(" ")
        print("# "*15)
        print(" ")

        if validate_yes_no(answear):
            break

    if answear.upper() == "Y":
        return True
    elif answear.upper() == "N":
        return False


def total(customer):
    order = customer.balance
    total = 0
    today = date.today().strftime("%d-%m-%Y")

    for value in order:
        total += value
        total = round(total, 2)

    return [today, total]


def user():
    """
    Code used when it is a user
    """
    print("Welcome to the Coders Bistro\n")

    is_registred_answear = is_registred()
    customer_data = need_to_be_register(is_registred_answear)
    customer = create_customer(customer_data)
    print("All done!")
    print(f'Welcome {customer.full_name()}')

    print("Would you like to check our menu? (Y / N)")
    while ordering():
        menu_option = menu_options()
        worksheet = select_worksheet(menu_option)
        display_menu(worksheet)
        id = customer_order(worksheet)
        value = get_value(id, worksheet)
        add_balance(customer, value)
        print("Anything else? (Y / N)")

    order = total(customer)
    update_worksheet(order, "sales")

    print("Thanks for eating with us!")
    print(f"The total of your order is ${order[1]}.")
    print(f'A copy of your order was send for {customer.email}')


def adm_user():
    print("LOADING SYSTEM...")
    sleep(2)
    print(" ")
    print("# "*15)
    print(" ")
    print("Do you want to log in as:")
    print("1 - Admin")
    print("2 - User")
    answear = input("Enter your answear here:\n")
    print(" ")
    print("# "*15)
    print(" ")
    while answear not in ("1", "2"):
        print("Please choose between one of the otpions.")
        answear = input("Enter your answear here:\n")

    return answear


def run_system(option):
    if option == "1":
        adm()
    elif option == "2":
        user()


def adm():
    email_password = adm_email_password()
    admin = Admin(email_password[0], email_password[1])
    option = adm_options()
    adm_functions(admin, option)


def adm_email_password():
    worksheet = select_worksheet("admin")
    print("First I need to check your email.")
    email = check_email(worksheet, 1)
    print("Now your password.")
    password = check_password(worksheet, 2)

    print("Validating data...")
    sleep(2)
    print("All good!")
    print(" ")
    print("# "*15)
    print(" ")

    return [email, password]


def check_password(sheet, col):
    """
    Check if the password is valid
    """
    worksheet = sheet
    password_collum = worksheet.col_values(col)

    while True:
        print("Can you write it for me?")
        password = input("Enter your answear here:\n")
        print(" ")
        print("# "*15)
        print(" ")

        if password in password_collum:
            break
        else:
            print("Wrong password.")
            print("Let's try again?\n")

    return password


def adm_options():

    print("What do you want to do today?")
    print("A - Check your Sales")
    print("B - Update Expanses")
    print("C - Check Expanses")
    print("D - Check your Total")
    option = input("Enter your answear here:\n").strip().upper()

    while option not in ("A", "B", "C", "D"):
        print("Choose between one of the otpions.")
        option = input("Enter your answear here:\n").strip().upper()

    print(" ")
    print("# "*15)
    print(" ")

    return option


def adm_functions(adm, option):

    if option == 'A':
        while True:
            print("Wich day do you want to check?")
            print("Ex: 30-07-2021")
            date = input("Enter your answear here:\n")
            total_sales = adm.check_sales(date)

            if total_sales:
                break
    elif option == "B":
        adm.new_expanse()
    elif option == 'C':
        while True:
            print("Wich day do you want to check?")
            print("Ex: 30-07-2021")
            date = input("Enter your answear here:\n")
            total_expenses = adm.check_expenses(date)

            if total_expenses:
                break


def main():
    option = adm_user()
    run_system(option)


main()
