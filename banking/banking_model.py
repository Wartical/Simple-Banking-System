import random
import sqlite3


class CardDataBase:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_last_emitted_card(self):
        if len(self.cards) > 0:
            return self.cards[-1]
        else:
            return Card(4000_0000_0000_0000, 0000)

    def is_card(self, card):
        return card in self.cards

    def get_card(self, number):
        for card in self.cards:
            if card.number == number:
                return card

        raise ValueError("No such card (number: {} )in database!".format(number))


class CardDataBaseSqlite3(CardDataBase):
    def __init__(self):
        super().__init__()
        self.connection = sqlite3.connect('card.s3db')
        self.cursor = self.connection.cursor()
        try:
            self.create_card_table()
        except sqlite3.OperationalError:
            return

    def create_card_table(self):
        self.cursor.execute(
            "CREATE TABLE card(\n" +
            "   id INTEGER,\n" +
            "   number TEXT,\n" +
            "   pin TEXT,\n" +
            "   balance INTEGER DEFAULT 0\n" +
            ")"
        )
        self.connection.commit()
        return

    def add_card(self, card):
        self.cursor.execute(
            f"INSERT INTO card (number, pin, balance) VALUES ({card.number}, {card.pin}, {card.account.balance})"
        )
        self.connection.commit()
        return

    def update_card(self, card):
        self.cursor.execute(
            f"UPDATE card SET\n"
            f"  number = {card.number},\n"
            f"  pin = {card.pin},\n"
            f"  balance = {card.account.balance}\n"
            f"WHERE\n"
            f"  number = {card.number}\n"
            f";"
        )
        self.connection.commit()
        return

    def get_card(self, number):
        self.cursor.execute(
            f"SELECT\n" +
            f"  number,\n" +
            f"  pin,\n" +
            f"  balance\n"
            f"FROM\n"
            f"  card\n"
            f"WHERE\n" +
            f"  number={number}\n"
            f";"
        )
        try:
            number, pin, balance = self.cursor.fetchone()
        except TypeError:
            raise ValueError("No such card (number: {} )in database!".format(number))

        card = Card(int(number), int(pin))
        card.account.balance = int(balance)
        return card

    def get_last_emitted_card(self):
        self.cursor.execute(
            f"SELECT\n" +
            f"  number,\n" +
            f"  pin,\n" +
            f"  balance\n"
            f"FROM\n"
            f"  card\n"
            f";"
        )
        try:
            number, pin, balance = self.cursor.fetchall()[-1]
        except IndexError:
            number = 4000_0000_0000_0000
            pin = 0000
            balance = 0

        card = Card(int(number), int(pin))
        card.account.balance = int(balance)
        return card

    def remove_card(self, card):
        self.cursor.execute(
            f"DELETE FROM card WHERE number={card.number} AND pin={card.pin}"
        )
        self.connection.commit()
        return


class CardFactory:
    def __init__(self, card_data_base):
        self.card_data_base = card_data_base

    def new_card(self):
        issuer_identification_number = 4000_00
        last_customer_id = str(self.card_data_base.get_last_emitted_card().get_customer_account_number())
        new_customer_id = str(int(last_customer_id) + 1).zfill(9)
        check_digit = self.compute_check_sum(issuer_identification_number, new_customer_id)
        new_id = int(
            str(issuer_identification_number) +
            str(new_customer_id) +
            str(check_digit)
        )

        pin = random.choice(range(10000))
        card = Card(new_id, pin)
        self.card_data_base.add_card(card)
        return card

    def compute_check_sum(self, issuer_identification_number, customer_id):
        initial_number = int(str(issuer_identification_number) + str(customer_id).zfill(9))
        initial_number = self.double_odd_digit(initial_number)
        sum = 0
        for digit in str(initial_number):
            sum += int(digit)

        check_sum = (10 - sum % 10) % 10
        return check_sum

    def double_odd_digit(self, number):
        output_number = ''
        for i, digit in enumerate(str(number)):
            if i % 2 == 0:
                double = 2 * int(digit)
                if double >= 10:
                    double -= 9

                output_number += str(double)
            else:
                output_number += digit

        return output_number

    def is_valid(self, number):
        issuer_identification_number = int(str(number)[:6])
        costumer_id = int(str(number)[6:-1])
        check_sum = self.compute_check_sum(issuer_identification_number, costumer_id)

        return check_sum == int(str(number)[-1])


class Card:
    def __init__(self, number, pin):
        self.number = number
        self.pin = pin
        self.account = Account()

    def get_issuer_identification_number(self):
        return int(str(self.number)[:6])

    def get_customer_account_number(self):
        return int(str(self.number)[6:-1])

    def get_checksum(self):
        return int(str(self.number)[-1])


class Account:
    def __init__(self, balance=0):
        self.balance = balance

    def deposit(self, amount):
        try:
            amount = self.validate_amount(amount)
        except ValueError:
            raise ValueError("Invalid amount ({}) for deposit!".format(amount))

        self.balance += amount
        return

    def withdraw(self, amount):
        try:
            amount = self.validate_amount(amount)
        except ValueError:
            raise ValueError("Invalid amount ({}) for withdraw!".format(amount))

        if self.balance < amount:
            raise ValueError("Not enough found to withdraw {}!".format(amount))

        self.balance -= amount
        return

    def validate_amount(self, amount):
        if amount < 0:
            raise ValueError

        return round(amount, 2)


class Logger:
    def __init__(self, card_data_base):
        self.card_data_base = card_data_base

    def log_to(self, card_number, pin):
        try:
            card = self.card_data_base.get_card(card_number)
        except ValueError:
            raise ValueError

        if card.pin == pin:
            return card
        else:
            raise ValueError('Wrong PIN!!')

    def is_valid_card_number(self, number):
        if len(str(number)) != 16:
            return False

        if int(str(number)[:6]) != 4000_00:
            return False

        return True
