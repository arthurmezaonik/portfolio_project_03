import gspread
from google.oauth2.service_account import Credentials
from email_validator import validate_email, EmailNotValidError
from datetime import date, datetime
from time import sleep

# Scope and fixed variables defined as love_sandwiches walkthrough project by Code Institute
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
    A class used to represent a Customer

    ...

    Attributes
    -----------
    first_name = str
        the customer's first name
    last_name = str
        the customer's last name
    email = str
        the customer's email
    order = list
        nested list with customer's order [name, value, quantity]
    
    Methods
    --------
    customer_full_name
        Return the customer full name
    customer_total
        Calculate and return the total from the order based on the order list    
    '''
    def __init__(self, first_name, last_name, email):
        """
        Instance attributes
        """
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.order = []

    def customer_full_name(self):
        """
        Return customer full name
        """
        return f'{self.first_name} {self.last_name}'

    def customer_total(self):
        """
        Calculate the total for the customer order
        """
        order = self.order
        total_order = 0
        today = date.today().strftime("%d-%m-%Y")

        for item in order:
            # Item value x item quantity
            item_total = item[1] * item[2]

            total_order += item_total
            total_order = round(total_order, 2)

        return [today, total_order]

    def customer_invoice(self):
        """
        Print the customer invoice
        """
        today = date.today().strftime("%d-%m-%Y")
        order = self.order
        total = self.customer_total()[1]

        print("Here it's your invoice:")
        print(" ")
        sleep(2)

        print("$" * 50)
        print(f'{today:>50}')
        print(" ")
        print(" "*18 + "CODER'S BISTRO" + " "*18)
        print(" ")
        print(f'Order for: {self.customer_full_name()}')
        print(f"Customer email: {self.email}")
        print(" ")
        print("-" * 50)
        print(" ")

        for item in order:
            print(f'{item[0]:<25} Quantity: {item[2]} {item[1]:>10}')

        print(" ")
        print("="*50)
        print('TOTAL' + ' '*38 + f'${total}')
        print("$" * 50)
        print(" ")


class Admin:
    '''
    A class used to represent a Admin

    ...

    Attributes
    -----------
    email = str
        the admin's email
    password = str
        the admin's password
    
    Methods
    --------
    check_sales
        Return the sale's total from the chosen day
    new_expense
        Collect value and description for a new expense and add to the expeses' worksheet
    check_expenses
        Return the expenses' total from the chosen day  
    '''
    def __init__(self, email, password):
        """
        Instance attributes
        """
        self.email = email
        self.password = password

    def check_sales(self, date):
        """
        Based on the chosen day, collect the sales from the worksheet.
        Return the sales' sum
        """
        sales_worksheet = select_worksheet("sales")
        day_column = sales_worksheet.col_values(1)
        sales = sales_worksheet.get_all_values()
        total = 0

        if date not in day_column:
            print(f"We don't have any sale register for {date}")

        else:
            for sale in sales:
                if sale[0] == date:
                    str_value = sale[1]
                    # Replace "," for "." so the string can be transformed in a float number
                    real_value = str_value.replace(",", ".")
                    total += float(real_value)

        return total

    def new_expense(self):
        """
        Collect a new expense's value and description
        Register the new expense on the expenses's worksheet
        """
        today = date.today().strftime("%d-%m-%Y")
        print("How much is the expnase?")
        print("Example: 15.50")
        value = validate_expense_value()
        print("Give a small description for your expense")
        description = input("Enter your answer here:\n")

        end_section()

        expense = [today, value, description]
        update_worksheet(expense, "expenses")

    def check_expenses(self, date):
        """
        Based on the chosen day, collect the expenses from the worksheet.
        Return the expenses' sum
        """
        expenses_worksheet = select_worksheet("expenses")
        day_column = expenses_worksheet.col_values(1)
        expenses = expenses_worksheet.get_all_values()
        total = 0

        if date not in day_column:
            print(f"We don't have an expense register for {date}")

        else:
            for expense in expenses:
                if expense[0] == date:
                    str_value = expense[1]
                    # Replace "," for "." so the string can be transformed in a float number
                    real_value = str_value.replace(",", ".")
                    total += float(real_value)

        return total


# CUSTOMER AND ADMIN FUNCTIONS
def login_or_register():
    """
    Check if the user wants to log in or register,
    And return the answer.
    """
    print("Do you want to:")
    print("1 - Log In")
    print("2 - Create an account")
    answer = input("Enter your answer here:\n").strip()

    end_section()

    # Validate if the answer is 1 or 2
    while answer not in ("1", "2"):
        print("Please choose between one of the options.")
        answer = input("Enter your answer here:\n").strip()

        end_section()

    return answer


def log_in():
    """
    Code used to do a log in
    """
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
            info = customer_info(user_email)
            customer = create_customer(info)
            customer_function(customer)
            break
        else:
            print("Sorry, I couldn't find your email")
            answer = email_not_found()
            # Try again
            if answer == "1":
                print("Can you write your email again?")
                pass
            # Register
            elif answer == "2":
                create_account()
                break


def collect_email():
    """
    Collect the user email
    """
    while True:
        email = input("Enter your answer here:\n").strip()

        end_section()

        if user_validate_email(email):
            break

    return email


def select_worksheet(option):
    """
    Based on the option, return the right worksheet
    """
    worksheet_dict = {
        "A" : 'food_menu',
        "B" : 'drink_menu',
        "C" : "deserts_menu",
        "ADMIN" : 'admin',
        "SALES" : 'sales',
        "EXPENSES" : 'expenses',
        'CLIENTS' : 'clients'
    }

    worksheet = ""
    
    for key, value in worksheet_dict.items():
        if option.upper() ==  key:
            worksheet = SHEET.worksheet(value)

    return worksheet


def update_worksheet(data, worksheet):
    """
    Receives a list to be inserted into a worksheet
    Update the relevant worksheet with the data provided
    """
    # Same function as used on the love_sandwiches walkthrough project by Code Institute
    worksheet_to_update = select_worksheet(worksheet)
    worksheet_to_update.append_row(data)


def find_row(item, worksheet):
    """
    Find the item's row in the specified worksheet
    """
    cell = worksheet.find(item)

    return cell.row


def end_section():
    '''
    Print a # line to end the sections
    '''
    print(" ")
    print("# "*25)
    print(" ")


# CUSTOMER FUNCTIONS
def create_account():
    """
    Code used to create a account
    """
    customer = register()
    customer_function(customer)


def register():
    """
    Register the user as a new customer.
    Return a Customer.    
    """
    print("Let's make a customer account for you!")
    print("I need some basic info.\n")
    customer_info = new_customer_info()
    update_worksheet(customer_info, "clients")

    return create_customer(customer_info)


def email_not_found():
    """
    Used when the system can't find the email.
    Check if the user want to try another email or create a new account,
    And return the answer
    """
    print("Do you want:")
    print("1 - Try again")
    print("2 - Create an account")
    answer = input("Enter your answer here:\n").strip()

    end_section()

    # Validate if the answer is 1 or 2
    while answer not in ("1", "2"):
        print("Invalid option, please choose between 1 or 2.")
        answer = input("Enter your answer here:\n").strip()

        end_section()

    return answer


def is_customer(email):
    """
    Check if email is from a customer account
    """
    customer_worksheet = select_worksheet('clients')
    email_column = customer_worksheet.col_values(3)

    if email in email_column:
        return True
    else:
        return False


def customer_info(email):
    """
    Collect the customer info from the clients worksheet
    Return a list with the customer info
    """
    customer_worksheet = select_worksheet('clients')
    user_email = email
    row = find_row(user_email, customer_worksheet)
    customer_info = customer_worksheet.row_values(row)

    return [customer_info[0], customer_info[1], customer_info[2]]


def new_customer_info():
    """
    Colect the customer info (first name, last name and email),
    And check if its not already registered.
    Return a lsit with the new customer info
    """
    client_worksheet = select_worksheet('clients')
    email_column = client_worksheet.col_values(3)

    print("What's your first name?")
    first_name = collect_name()
    print("What's your last name?")
    last_name = collect_name()
    print("What's your email?")

    while True:
        email = collect_email()

        # Check if email is already registered
        if email not in email_column:
                break
        else:
            print("Sorry, this email is already in use")
            print("Can we try again?\n")

    return [first_name, last_name, email]


def collect_name():
    '''
    Collect the user first and last name
    '''
    while True:
        name = input("Enter your answer here:\n").capitalize().strip()

        end_section()

        if validate_name(name):
            break
    
    return name


def create_customer(data):
    """
    Create the customer
    """
    return Customer(data[0], data[1], data[2])


def menu_options():
    """
    Print the menu's names and check which one the user want to check
    Return the answer
    """
    print("Which menu do you want to check?")
    print("A - Foods menu")
    print("B - Drinks menu")
    print("C - Deserts menu")
    menu_option = input("Enter your answer here:\n").upper().strip()

    end_section()
    
    #Validate if the answer is A, B or C
    while menu_option not in ("A", "B", "C"):
        print("Please choose one of the options:")
        print("A - Foods menu")
        print("B - Drinks menu")
        print("C - Deserts menu")
        menu_option = input("Enter your answer here:\n").upper().strip()

        end_section()

    return menu_option


def display_menu(worksheet):
    """
    Print the chosen menu on the screen
    """
    menu_worksheet_values = worksheet.get_all_values()

    for item in menu_worksheet_values:
        print(f'{item[0]:<5}{item[1]:_<20}{item[2]:_>20}')


def customer_order(worksheet):
    """
    Collect the ID from the item that the customer wnats
    Return the ID
    """
    while True:
        print("What's the ID from the item that you want?")
        id = input("Enter your answer here:\n").strip()

        end_section()

        if validate_order(id, worksheet):
            break

    return id


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

    return float(item_row[2])


def item_quantity():
    """
    Return the desired quantity from the chosen item
    """
    print("How many do you want?")
    print("Ex: 8 ")
    quantity = input("Enter your answer here: \n").strip()

    end_section()

    while not validate_item_quantity(quantity):
        quantity = input("Enter your answer here: \n").strip()

        end_section()

    return int(quantity)


def add_order(customer, item):
    """
    Add item on the customer order
    """
    customer.order.append(item)


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
    order = customer.order
    total_order = 0
    today = date.today().strftime("%d-%m-%Y")

    for item in order:
        # Item value x item quantity
        item_total = item[1] * item[2]

        total_order += item_total
        total_order = round(total_order, 2)

    return [today, total_order]


def customer_function(customer):
    """
    Code used when the user is a customer
    """
    print("All done!")
    print(f'Welcome {customer.customer_full_name()}')

    # While loop to print the menu on the screen and collect the customer order
    # Item's value added to the customer order
    print("Would you like to check our menu? (Y / N)")
    while ordering():
        # Display menu
        menu_option = menu_options()
        menu_worksheet = select_worksheet(menu_option)
        display_menu(menu_worksheet)

        # Select item
        item_id = customer_order(menu_worksheet)
        item_row = find_row(item_id, menu_worksheet)

        # From ID and row get item informations
        plate = item_name(item_row, menu_worksheet)
        value = item_value(item_row, menu_worksheet)
        quantity = item_quantity()
        item = [plate, value, quantity]
        print("Noted!\n")

        add_order(customer, item)
        print("Anything else? (Y / N)")

    # Farewell message
    farewell_message = customer_farewell_message(customer)
    print(farewell_message)


def customer_farewell_message(customer):
    '''
    Displays a fareweel message depending on the final balance
    If balance > 0, add the sale on the sales worksheet
    '''
    # Generate the final order
    total_order = customer.customer_total()
    order_value = total_order[1]

    if order_value == 0:
        return 'Thanks for visiting.\nWe hope you come back soon.'
    elif order_value > 0:
        # Add order on the sales worksheet
        update_worksheet(total_order, "sales")
        customer.customer_invoice()
        return 'Thanks for eating with us!'


#ADMIN FUNCTIONS
def is_admin(email):
    """
    Check if email is from a admin account
    """
    admin_worksheet = select_worksheet('admin')
    email_column = admin_worksheet.col_values(1)

    if email in email_column:
        return True
    else:
        return False


def collect_admin_password():
    """
    Collect and validate admin's password
    """
    admin_worksheet = select_worksheet("admin")
    password_column = admin_worksheet.col_values(2)
    print("Now your password.")

    while True:
        password = input("Enter your answer here:\n").strip()

        end_section()

        if password in password_column:
            break
        else:
            print("Wrong password.")
            print("Let's try again?\n")

    return password


def admin_options():
    """
    From the admin's options, check what he wants to do,
    And return the answer
    """
    print("What do you want to do today?")
    print("A - Check your Sales")
    print("B - Update Expenses")
    print("C - Check Expenses")
    print("D - Check your Total")
    option = input("Enter your answer here:\n").strip().upper()

    end_section()

    # Validate if the answer is A, B, C or D
    while option not in ("A", "B", "C", "D"):
        print("Choose between one of the options.")
        option = input("Enter your answer here:\n").strip().upper()

        end_section()

    return option


def admin_functions(adm, option):
    """
    From the admin option, execute the right code
    """
    # Check the sales' total
    if option == 'A':
        date = collect_date()
        total_sales = adm.check_sales(date)

        print(f"The sales' total in {date} is ${total_sales:.2f}")

    # Create a new expense
    elif option == "B":
        adm.new_expense()

    # Check the expenses' total
    elif option == 'C':
        date = collect_date()
        total_expenses = adm.check_expenses(date)

        print_expenses(date)
        print(f"The expenses' total in {date} is ${total_expenses:.2f}")

    # Display the day balance
    elif option == "D":
        day_balance(adm)


def collect_date():
    '''
    Collect a date to be checked
    '''
    print("Which day do you want to check?")
    print("Ex: July 30th, 2021 would be 30-07-2021")
    date = input("Enter your answer here:\n").strip()

    end_section()

    while not validate_date(date):
        date = input("Enter your answer here:\n").strip()

        end_section()

    return date


def print_expenses(date):
    """
    From the chosen day,
    Collect the expenses on the expenses' worksheet and print on the terminal
    """
    expenses_worksheet = select_worksheet("expenses")
    expenses = expenses_worksheet.get_all_values()

    header = expenses[0]
    print(f'{header[0]:<15}{header[1]:<15}{header[2]:<20}')

    for expense in expenses:
        if expense[0] == date:
            print(f'{expense[0]:<15}${expense[1]:<14}{expense[2]:<20}')
    print("")


def day_balance(adm):
    """
    Print the total balance from the chosen day
    """
    date = collect_date()

    sales = adm.check_sales(date)
    expenses = adm.check_expenses(date)

    total = sales - expenses

    print(f'In {date} you sold ${sales} and spent ${expenses}.')
    print(f'Your total is ${total:.2f}.')


def working():
    """
    Check if the admin wants to keep working
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


def admin_function(email):
    """
    Code used when the user is a admin
    """
    # Create a Admin
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


#VALIDATIONS
def validate_expense_value():
    '''
    Validate the expanses value.
    Check if can be transformed in a float number
    '''
    value = input("Enter your answer here:\n")

    end_section()

    while True:
        try:
            float(value)
            valid_value = float(value)
            break
        except ValueError:
            print('Invalid value, please use "." symbol')
            print("Examples: 1100, 10.50, 2537.72")
            value = input("Enter your answer here:\n")

            end_section()

    return valid_value


def user_validate_email(email):
    """
    Validate the email address.
    Check if follows the email pattern ____@xxx.xx
    """
    try:
        validate_email(email)

        return True

    except EmailNotValidError as e:
        print(str(e))
        print("Example: code@codersbistro.com")
        print('Lets try again')


def validate_name(name):
    '''
    Validate customer name
    Check if the name is at least 1 char long    
    '''
    try:
        if len(name) < 1:
            raise ValueError ("Your name needs to be at least one char long.")

    except ValueError as e:
        print(f"Incorrect input: {e} Please try again.")
        return False
    
    return True


def validate_order(id, worksheet):
    """
    Validate order
    Check if the item's ID is on the list
    """
    ids = worksheet.col_values(1)

    try:
        if id not in ids:
            raise ValueError("Choose between one of the printed Ids")
    except ValueError as e:
        print(f"Invalid option: {e}, please try again.\n")
        return False

    return True


def validate_item_quantity(quantity):
    """
    Validate order's quantity
    Check if the quantity is a int number
    """
    try:
        int(quantity)
        return True
    except ValueError:
        print("Please enter a integer number")
        print("Ex: 8")


def validate_date(date):
    '''
    Validate date
    Check if the date is in the right format DD-MM-YYYY
    '''
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
    Check if the answer is Y or N
    """
    try:
        if answer not in ("Y", "N"):
            raise ValueError('Choose between Y or N')

    except ValueError as e:
        print(f"Invalid data: {e}, please try again.")
        return False

    return True


def main():
    """
    Run the main code
    """
    # Welcome message
    print("WELCOME TO CODER'S BISTRO")
    sleep(2)

    end_section()

    # Login or register
    user_option = login_or_register()

    # Run the system based on the otpion
    # Log in option
    if user_option == "1":
        log_in()

    # Register option
    elif user_option == "2":
        create_account()

main()
