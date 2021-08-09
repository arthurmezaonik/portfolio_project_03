import gspread
from google.oauth2.service_account import Credentials
from datetime import date, datetime
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
    '''
    Create a customer
    '''
    def __init__(self, f_name, l_name, email):
        # Instance attributes
        self.f_name = f_name
        self.l_name = l_name
        self.email = email
        self.balance = []

    def info(self):
        """
        Return the clients full info
        """
        return (f'Client: {self.full_name()}. Email: {self.email}. Balance: {self.balance}')

    def full_name(self):
        """
        Return customer name
        """
        return f'{self.f_name} {self.l_name}'


class Admin:
    """
    Create a admin
    """
    def __init__(self, email, password):
        # Instance attributes
        self.email = email
        self.password = password

    def info(self):
        """
        Return admin info
        """
        return f'Email: {self.email} Password: {self.password}'

    def check_sales(self, date):
        """
        Check the sum of the sales from the chosen day
        """
        worksheet = select_worksheet("sales")
        day_col = worksheet.col_values(1)
        sales = worksheet.get_all_values()
        total = 0

        if date not in day_col:
            print(f"We don't have any sale register for {date}")

            return [total, True]
        else:
            for sale in sales:
                if sale[0] == date:
                    num_sheet = sale[1]
                    num = num_sheet.replace(",", ".")
                    total += float(num)

            return [total, True]

    def new_expense(self):
        """
        Register a new expense on the worksheet
        """
        today = date.today().strftime("%d-%m-%Y")
        print("How much is the expnase?")
        print("Example: 15.50")
        value = float(input("Enter your answer here:\n"))
        print("Give a small description for your expense")
        description = input("Enter your answer here:\n")

        data = [today, value, description]
        update_worksheet(data, "expenses")

    def check_expenses(self, date):
        """
        Check the sum of the expenses from the chosen day
        """
        worksheet = select_worksheet("expenses")
        day_col = worksheet.col_values(1)
        expenses = worksheet.get_all_values()
        total = 0

        if date not in day_col:
            print(f"We don't have an expense register for {date}")

            return [total, True]
        else:
            for expense in expenses:
                if expense[0] == date:
                    num_sheet = expense[1]
                    num = num_sheet.replace(",", ".")
                    total += float(num)

            return [total, True]


def login_or_register():
    """
    Ask if the user wants to log in or register
    """
    print("Do you want to:")
    print("1 - Log In")
    print("2 - Create an account")
    answer = input("Enter your answer here:\n").strip()

    end_section()

    while answer not in ("1", "2"):
        print("Please choose between one of the options.")
        answer = input("Enter your answer here:\n").strip()

    return answer


def run_system(option):
    """
    Run the code based on the given option
    """
    user_option = option

    # Log in option
    if user_option == "1":
        print("Good to have you back!")
        print("I just need to check your email.")
        print("Can you write it for me?")

        while True:
            user_email = collect_email()
            admin = is_admin(user_email)
            customer = is_customer(user_email)
            # If it is a admin email
            if admin:
                admin_function(user_email)
                break
            # If it is a customer email
            elif customer:
                data = customer_data(user_email)
                customer_function(data)
                break
            else:
                print("Sorry, I couldn't find your email")
                answer = try_again_question()
                # Try again
                if answer == "1":
                    print("Can you write your email again?")
                    pass
                # Register
                elif answer == "2":
                    register()
                    break

    # Register option
    elif user_option == "2":
        register()


def register():
    """
    Register the user as a new client
    """
    print("Let's make a customer account for you!")
    print("I need some basic info.\n")
    data = new_customer_data()
    update_worksheet(data, "clients")
    customer_function(data)


def try_again_question():
    print("Do you want:")
    print("1 - Try again")
    print("2 - Create an account")
    answer = ""

    while answer not in ("1", "2"):
        print("Invalid option, please choose between 1 or 2.")
        answer = input("Enter your answer here:\n").strip()

        end_section()

    return answer


def collect_email():
    """
    Collect the user email
    """
    while True:
        email = input("Enter your answer here:\n").strip()

        end_section()

        if validate_email(email):
            break

    return email


def validate_email(email):
    """
    Validate if email has a @ sign
    """
    try:
        if "@" not in email:
            raise ValueError("Please enter a valid email")
    except ValueError as e:
        print(f"Invalid data: {e}")
        print("Example: code@codersbistro.com\n")
        return False

    return True


def is_admin(email):
    """
    Check if email is from a admin account
    """
    admin_sheet = select_worksheet('admin')
    email_col = admin_sheet.col_values(1)

    if email in email_col:
        return True
    else:
        return False


def is_customer(email):
    """
    Check if email is from a customer account
    """
    customer_sheet = select_worksheet('clients')
    email_col = customer_sheet.col_values(3)

    if email in email_col:
        return True
    else:
        return False


def select_worksheet(option):
    """
    From the option, select the needed worksheet
    """
    worksheet = ""

    # Food worksheet
    if option.upper() == "A":
        worksheet = SHEET.worksheet("food_menu")
    # Drinks worksheet
    elif option.upper() == "B":
        worksheet = SHEET.worksheet("drink_menu")
    # Deserts worksheet
    elif option.upper() == "C":
        worksheet = SHEET.worksheet("deserts_menu")
    # Admin worksheet
    elif option.upper() == "ADMIN":
        worksheet = SHEET.worksheet("admin")
    # Sales worksheet
    elif option.upper() == "SALES":
        worksheet = SHEET.worksheet("sales")
    # Expenses worksheet
    elif option.upper() == "EXPENSES":
        worksheet = SHEET.worksheet("expenses")
    # Clients worksheet
    elif option.upper() == "CLIENTS":
        worksheet = SHEET.worksheet("clients")
    else:
        print("Worksheet name problem")

    return worksheet


def update_worksheet(data, worksheet):
    """
    Receives a list of integers to be inserted into a worksheet
    Update the relevant worksheet with the data provided
    """
    worksheet_to_update = select_worksheet(worksheet)
    worksheet_to_update.append_row(data)


def customer_function(data):
    """
    Code used when it is a customer
    """
    # Create a customer from the collected data
    customer = create_customer(data)
    print("All done!")
    print(f'Welcome {customer.full_name()}')

    # While loop to print the menu on the screen and collect the customer order
    # Item' value added to the customer balance
    print("Would you like to check our menu? (Y / N)")
    while ordering():
        # Display menu
        menu_option = menu_options()
        menu_sheet = select_worksheet(menu_option)
        display_menu(menu_sheet)
        # Select item
        item_id = customer_order(menu_sheet)
        item_row = find_row(item_id, menu_sheet)
        # From ID and row get item informations
        plate = item_name(item_row, menu_sheet)
        value = item_value(item_row, menu_sheet)
        quantity = item_quantity()
        order = [plate, value, quantity]
        print(order)
        print("Noted!\n")

        add_balance(customer, order[1])
        print("Anything else? (Y / N)")

    # Farewell message
    farewell_message = customer_farewell_message(customer)
    print(farewell_message)


def customer_data(email):
    """
    Collect the customer data from the worksheet
    """
    customer_sheet = select_worksheet('clients')
    user_email = email
    row = find_row(user_email, customer_sheet)
    customer_data = customer_sheet.row_values(row)

    return [customer_data[0], customer_data[1], customer_data[2]]


def new_customer_data():
    """
    Colect customer data and check if its not already registered
    """
    client_sheet = select_worksheet('clients')
    email_column = client_sheet.col_values(3)

    f_name = input("What's your first name?\n").capitalize().strip()
    l_name = input("What's your last name?\n").capitalize().strip()

    while True:
        email = input("What's your email?\n").strip()

        if email not in email_column:
            if validate_email(email):
                break
        else:
            print("Sorry, this email is already in use")
            print("Can we try again?\n")

    end_section()

    return [f_name, l_name, email]


def find_row(item, sheet):
    """
    Find the item's row in the specified worksheet
    """
    worksheet = sheet
    cell = worksheet.find(item)

    return cell.row


def create_customer(data):
    """
    Create the customer
    """
    return Customer(data[0], data[1], data[2])


def menu_options():
    """
    Present the menus and return user otpion
    """
    print("Which menu do you want to check?")
    print("A - Foods menu")
    print("B - Drinks menu")
    print("C - Deserts menu")
    menu_option = input("Enter your answer here:\n").upper().strip()

    end_section()

    while menu_option not in ("A", "B", "C"):
        print("Please choose one of the options:")
        print("A - Foods menu")
        print("B - Drinks menu")
        print("C - Deserts menu")
        menu_option = input("Enter your answer here:\n").upper().strip()

        end_section()

    return menu_option


def display_menu(sheet):
    """
    Print the chosen menu on the screen
    """
    menu_sheet = sheet.get_all_values()

    for item in menu_sheet:
        print(f'{item[0]:<5}{item[1]:_<20}{item[2]:_>20}')


def customer_order(worksheet):
    """
    Collect the customer order
    """
    while True:
        print("What's the ID from the item that you want?")
        id = input("Enter your answer here:\n").strip()

        end_section()

        if validate_order(id, worksheet):
            break

    return id


def validate_order(id, worksheet):
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


def item_name(row, sheet):
    """
    Return the name from the chosen item
    """
    item_row = sheet.row_values(row)

    return item_row[1]


def item_value(row, sheet):
    """
    Return the value from the chosen item
    """
    item_row = sheet.row_values(row)

    return item_row[2]


def item_quantity():
    """
    Return the quantity from the chosen item
    """
    print("How many do you want?")
    print("Ex: 8 ")
    quantity = input("Enter your answear here: \n").strip()

    end_section()

    while not validate_item_quantity(quantity):
        quantity = input("Enter your answear here: \n").strip()

        end_section()

    return quantity


def validate_item_quantity(quantity):
    """
    Validate if the quantity is a int number
    """
    try:
        int(quantity)
        return True
    except ValueError:
        print("Please enter a hole number")
        print("Ex: 8")


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
        answer = input("Enter your answer here:\n").strip().upper()

        end_section()

        if validate_yes_no(answer):
            break

    if answer == "Y":
        return True
    elif answer == "N":
        return False


def total(customer):
    """
    Calculate the total for the customer order
    """
    order = customer.balance
    total = 0
    today = date.today().strftime("%d-%m-%Y")

    for value in order:
        total += value
        total = round(total, 2)

    return [today, total]


def customer_farewell_message(customer):
    '''
    Displays a fareweel message depending on the final balance
    If balance > 0, add the sale on the sales worksheet
    '''
    # Generate the final order
    order = total(customer)
    order_value = order[1]

    if order_value == 0:
        return 'Thanks for visiting.\nWe hope you come back soon.'
    elif order_value > 0:
        # Add order on the sales worksheet
        update_worksheet(order, "sales")
        return 'Thanks for eating with us!'
    else:
        return 'Error message: farewell function.'


def admin_function(email):
    admin_email = email
    admin_password = collect_admin_password()
    admin = Admin(admin_email, admin_password)

    print("Logged in as ADMIN\n")
    print("Do you want to check your options?(Y / N)")
    while working():
        option = admin_options()
        admin_functions(admin, option)
        print("Do you want to check anything else?(Y / N)")

    print("System ended.")


def collect_admin_password():
    """
    Collect and validate admin's password
    """
    admin_sheet = select_worksheet("admin")
    password_col = admin_sheet.col_values(2)
    print("Now your password.")

    while True:
        password = input("Enter your answer here:\n").strip()

        end_section()

        if password in password_col:
            break
        else:
            print("Wrong password.")
            print("Let's try again?\n")

    return password


def admin_options():
    """
    Displays admin options
    """
    print("What do you want to do today?")
    print("A - Check your Sales")
    print("B - Update Expenses")
    print("C - Check Expenses")
    print("D - Check your Total")
    option = input("Enter your answer here:\n").strip().upper()

    while option not in ("A", "B", "C", "D"):
        print("Choose between one of the options.")
        option = input("Enter your answer here:\n").strip().upper()

    end_section()

    return option


def admin_functions(adm, option):
    """
    From the admin option, execute the code
    """
    # Check the sales' total
    if option == 'A':
        while True:
            date = collect_date()

            if validade_date(date):
                total_sales = adm.check_sales(date)
                if total_sales[1]:
                    break

        print(f"The sales' total in {date} is ${total_sales[0]}")

    # Create a new expense
    elif option == "B":
        adm.new_expense()

    # Check the expenses' total
    elif option == 'C':
        while True:
            date = collect_date()

            if validade_date(date):
                total_expenses = adm.check_expenses(date)
                if total_expenses[1]:
                    break

        print_expenses(date)
        print(f"The expenses' total in {date} is ${total_expenses[0]}")

    # Display the day balance
    elif option == "D":
        print(day_balance(adm))


def collect_date():
    '''
    Collect the date and validate it.
    '''
    print("Which day do you want to check?")
    print("Ex: July 30th, 2021 would be 30-07-2021")
    date = input("Enter your answer here:\n").strip()

    return date


def print_expenses(date):
    """
    From the worksheet, display the expenses
    """
    worksheet = select_worksheet("expenses")
    expenses = worksheet.get_all_values()

    header = expenses[0]
    print(f'{header[0]:<15}{header[1]:<10}{header[2]:<20}')

    for expense in expenses:
        if expense[0] == date:
            print(f'{expense[0]:<15}${expense[1]:<9}{expense[2]:<20}')
    print("")


def day_balance(adm):
    """
    Print the total balance from the chosen day
    """
    while True:
        date = collect_date()

        if validade_date(date):
            break

    sales = adm.check_sales(date)[0]
    expenses = adm.check_expenses(date)[0]

    total = sales - expenses

    return f'In {date} you sold ${sales} and spent ${expenses}. Your total is ${total}.'


def working():
    """
    Check if the admin want to keep working
    """
    while True:
        answer = input("Enter your answer here:\n").strip().upper()

        end_section()

        if validate_yes_no(answer):
            break

    if answer == "Y":
        return True
    elif answer == "N":
        return False


def validade_date(date):
    date_str = date

    try:
        datetime.strptime(date_str, '%d-%m-%Y')
        return True

    except ValueError:
        print("Incorrect date format. It should be DD-MM-YYYY.")
        return False


def validate_yes_no(answer):
    """
    Validate yes or no questions
    """
    try:
        if answer not in ("Y", "N"):
            raise ValueError('Choose between Y or N')

    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")
        return False

    return True


def end_section():
    '''
    Print a # line to end the sections
    '''
    print(" ")
    print("# "*15)
    print(" ")


def main():
    """
    Run the main code
    """
    # Welcome message
    print("WELCOME TO CODER'S BISTRO")
    sleep(2)

    end_section()

    # Login or register
    log_register = login_or_register()
    # Run the system based on the otpion
    run_system(log_register)


main()
