import os
import sqlite3
from loader import Utility
from flask import session
from validate import validate_dob, validate_fullname, validate_id_number, validate_phone_number
from time import sleep


class UserFlow:
    def __init__(self):
        self.conn = sqlite3.connect(os.getenv('DB_NAME'))
        self.c = self.conn.cursor()
        self.create_db()

    def create_db(self):
        # Create table if not exists
        self.c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     fullname TEXT,
                     phone_number TEXT,
                     id_number TEXT,
                     dob TEXT,
                     address TEXT,
                     balance REAL,
                     policy_type TEXT,
                     policy_number TEXT)''')
        self.conn.commit()

    async def process(self, user_input):
        if 'authenticated' not in session:
            if 'registration_step' in session:
                if session['registration_step'] == 1:
                    if not validate_fullname(user_input):
                        sleep(2) # delay response
                        return "Invalid input😒. Please enter a valid full name (at least 4 characters, no special characters, no numbers)."
                    session['registration_data']['fullname'] = user_input
                    session['registration_step'] = 2
                    sleep(2)  # delay response
                    return "Please enter your phone number (starting with 07 and exactly 10 digits)."
                elif session['registration_step'] == 2:
                    if not validate_phone_number(user_input):
                        sleep(2)  # delay response
                        return "Invalid input😒. Please enter a valid phone number (starting with 07 and exactly 10 digits)."
                    session['registration_data']['phone_number'] = user_input
                    session['registration_step'] = 3
                    sleep(2)  # delay response
                    return "Please enter your ID number (format: 00-000000A00)."
                elif session['registration_step'] == 3:
                    if not validate_id_number(user_input):
                        sleep(2)  # delay response
                        return "Invalid input😒. Please enter a valid ID number (format: 00-000000A00)."
                    session['registration_data']['id_number'] = user_input
                    session['registration_step'] = 4
                    sleep(2)  # delay response
                    return "Please enter your date of birth (YYYY-MM-DD)."
                elif session['registration_step'] == 4:
                    if not validate_dob(user_input):
                        sleep(2)  # delay response
                        return "Invalid input😒. Please enter a valid date of birth (YYYY-MM-DD)."
                    session['registration_data']['dob'] = user_input
                    session['registration_step'] = 5
                    sleep(2)  # delay response
                    return "Please enter your address (at least 5 characters)."
                elif session['registration_step'] == 5:
                    if len(user_input) < 5:
                        sleep(2)  # delay response
                        return "Invalid input😒. Address should be at least 5 characters long."
                    session['registration_data']['address'] = user_input
                    session['registration_step'] = 6
                    return "Please enter the type of policy (at least 5 characters)."
                elif session['registration_step'] == 6:
                    if len(user_input) < 5:
                        sleep(2)  # delay response
                        return "Invalid input😒. Policy type should be at least 5 characters long."
                    session['registration_data']['policy_type'] = user_input
                    policy_number = self.register_user(session['registration_data'])
                    session['authenticated'] = True
                    session['current_user'] = session['registration_data']
                    session.pop('registration_step', None)
                    session.pop('registration_data', None)
                    return f'Registration successful👏👏👏! Your policy number is {policy_number}. You are now logged in.'

            elif 'login_step' in session:
                if session['login_step'] == 1:
                    if not validate_phone_number(user_input):
                        sleep(2)  # delay response
                        return "Invalid input😒. Please enter a valid phone number (starting with 07 and exactly 10 digits)."
                    session['login_data'] = {}
                    session['login_data']['phone_number'] = user_input
                    session['login_step'] = 2
                    sleep(2)  # delay response
                    return "Please enter your ID number (format: 00-000000A00)."
                elif session['login_step'] == 2:
                    if not validate_id_number(user_input):
                        sleep(2)  # delay response
                        return "Invalid input😒. Please enter a valid ID number (format: 00-000000A00)."
                    session['login_data']['id_number'] = user_input
                    user = self.login_user(session['login_data'])
                    if user is not None:
                        session['authenticated'] = True
                        session['current_user'] = user
                        session.pop('login_step', None)
                        session.pop('login_data', None)
                        sleep(2)  # delay response
                        return "Thank you for signing in. I now have access to your account☺️"
                    else:
                        session['login_step'] = 1
                        session['login_data'] = {}
                        sleep(2)  # delay response
                        return "Hmmm👎🏿, you have supplied incorrect details, login failed. Please enter your phone number."

            if user_input.lower() in ['no', "i don't have an account", 'nope', "i don't have one"]:
                session['registration_step'] = 1
                session['registration_data'] = {}
                sleep(2)  # delay response
                return "Cooool👍!, Let's start the registration process. Please enter your full name."
            elif user_input.lower() in ['yes', 'yes, i have an account', 'yep', 'yess.']:
                session['login_step'] = 1
                session['login_data'] = {}
                sleep(2)  # delay response
                return "Cooolies👍, Let's start the login process. Please enter your phone number."
            else:
                session['authenticated'] = True
                session['current_user'] = 'No user account information available as the user is logged in as a guest'
                sleep(2)  # delay response
                return "Awesome😎, How may I assist you today?"
        else:
            user = session['current_user']
            if user is not None:
                filepath = "content/data/model.txt"
                vectorpath = "content/vectors"
                filename = "model.txt"
                utility = Utility(filepath=filepath, vectorpath=vectorpath, filename=filename, query=user_input, account_details=user)
                response = await utility.answer()
                return str(response)
            else:
                sleep(2)  # delay response
                return "Hmmmm...., I am lost here, Please try again."

    # Registration function
    def register_user(self, data):
        policy_number = data['fullname'][0] + data['dob'].replace('-', '')
        balance = 0
        self.c.execute(
            "INSERT INTO users (fullname, phone_number, id_number, dob, address, balance, policy_type, policy_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (data['fullname'], data['phone_number'], data['id_number'], data['dob'], data['address'], balance,
             data['policy_type'], policy_number))
        self.conn.commit()
        return policy_number

    # Login function
    def login_user(self, data):
        self.c.execute("SELECT * FROM users WHERE phone_number=? AND id_number=?",
                       (data['phone_number'], data['id_number']))
        user = self.c.fetchone()
        if user:
            column_names = [description[0] for description in self.c.description]
            return dict(zip(column_names, user))
        return None
