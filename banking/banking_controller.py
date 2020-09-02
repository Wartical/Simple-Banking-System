from banking.banking_model import Logger, CardFactory, CardDataBaseSqlite3, Card


class Controller:
    def __init__(self, diplayer, retriever):
        self.displayer = diplayer
        self.retriever = retriever
        self.choices = ['choice 1', 'choise 2']

    def witch_choices(self):
        message = ''
        for choice in self.choices:
            message += '\n' + choice

        return self.retriever.retrieve(message)


class MainMenuController(Controller):
    def __init__(self, displayer, retriever, card_factory, logger):
        super().__init__(displayer, retriever)
        self.choices = ['1. Create an account', '2. Log into account', '0. Exit']
        self.is_over = False
        self.card_factory = card_factory
        self.logger = logger

    def main_loop(self):
        user_choice = self.witch_choices()
        if user_choice == '0':
            self.is_over = True
            self.displayer.display("Bye!")
            return

        if user_choice == '1':
            self.create_account()
            return self.main_loop()

        if user_choice == '2':
            number = int(self.retriever.retrieve("\nEnter your card number:"))
            pin = int(self.retriever.retrieve("\nEnter your PIN:"))
            try:
                card = self.logger.log_to(number, pin)
                self.displayer.display("\nYou have successfully logged in!")
                return card
            except ValueError:
                self.displayer.display("\nWrong card number or PIN!")
                return self.main_loop()

        self.main_loop()

    def create_account(self):
        card = self.card_factory.new_card()
        self.displayer.display(
            f"\nYour card have been created\n" +
            f"Your card number:\n" +
            f"{card.number}\n" +
            f"Your card PIN:\n" +
            f"{str(card.pin).zfill(4)}"
        )
        return card


class LoggedInController(Controller):
    def __init__(self, displayer, retriever, card, card_data_base, card_factory):
        super().__init__(displayer, retriever)
        self.choices = ['1. Balance', '2. Add income', '3. Do transfer', '4. Close account', '5. Log out', '0. Exit']
        self.is_over = False
        self.card = card
        self.card_data_base = card_data_base
        self.card_factory = card_factory

    def main_loop(self):
        user_choice = self.witch_choices()
        if user_choice == '0':
            self.is_over = True
            self.displayer.display("Bye!")
            return

        if user_choice == '1':
            self.displayer.display(f"\nBalance: {self.card.account.balance}")

        if user_choice == '2':
            income = int(self.retriever.retrieve("\nEnter income:"))
            self.card.account.deposit(income)
            self.card_data_base.update_card(self.card)
            self.displayer.display("Income was added!")

        if user_choice == '3':
            self.displayer.display("\nTransfer")
            number = int(self.retriever.retrieve("Enter card number:"))
            if not self.card_factory.is_valid(number):
                self.displayer.display("Probably you made a mistake in the card number. Please try again!")
                return self.main_loop()

            try:
                target_card = self.card_data_base.get_card(number)
                amount_to_transfer = int(self.retriever.retrieve("Enter how much money you want to transfer:"))
                self.displayer.display("Success!")
                try:
                    self.card.account.withdraw(amount_to_transfer)
                    target_card.account.deposit(amount_to_transfer)
                except ValueError:
                    self.displayer.display("Not enough money!")
                self.card_data_base.update_card(self.card)
                self.card_data_base.update_card(target_card)
            except ValueError:
                self.displayer.display("Such a card does not exist.")

        if user_choice == '4':
            self.displayer.display("\nThe account has been closed!")
            self.card_data_base.remove_card(self.card)
            return

        if user_choice == '5':
            self.displayer.display("\nYou have successfully logged out!")
            self.is_over = False
            return

        self.main_loop()