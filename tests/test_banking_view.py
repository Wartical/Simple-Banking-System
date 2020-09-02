import unittest
import _context
import sys
from io import StringIO
from banking.banking_view import MenuPage, LoggedInPage, AccountCreatedPage,\
    CardNumberPage, PinPage, BalancePage, LogOutPage, ExitPage


class TestPage(unittest.TestCase):
    def setUp(self):
        self.captured_output = StringIO()
        self.old_stdout = sys.stdout
        sys.stdout = self.captured_output  # redirect stdout

    def tearDown(self):
        sys.stdout = self.old_stdout


class TestMenuPage(TestPage):
    def test_page(self):
        self.menu_page = MenuPage()
        self.menu_page.display()
        captured_string = self.captured_output.getvalue()
        self.assertEqual(
            "\n1. Create an account\n2. Log into account\n0. Exit\n", captured_string)


class TestLoggedInPage(TestPage):
    def test_page(self):
        self.logged_in_page = LoggedInPage()
        self.logged_in_page.display()
        self.assertEqual(
            "\n1. Balance\n2. Log out\n0. Exit\n", self.captured_output.getvalue())


class TestAccountCreatedPage(TestPage):
    def test_page(self):
        self.account_created_page = AccountCreatedPage()
        self.account_created_page.set_number(4000_0011_1111_1112)
        self.account_created_page.set_pin(0000)
        self.account_created_page.display()
        self.assertEqual(
            "\nYour card has been created\nYour card number:\n4000001111111112\nYour card PIN:\n0000\n",
            self.captured_output.getvalue()
        )


class TestCardNumberPage(TestPage):
    def test_page(self):
        self.card_number_page = CardNumberPage()
        self.card_number_page.display()
        self.assertEqual(
            "\nEnter your card number:\n",
            self.captured_output.getvalue()
        )


class TestPinPage(TestPage):
    def test_page(self):
        self.pin_page = PinPage()
        self.pin_page.display()
        self.assertEqual(
            "Enter your PIN:\n",
            self.captured_output.getvalue()
        )


class TestExitPage(TestPage):
    def test_page(self):
        self.exit_page = ExitPage()
        self.exit_page.display()
        self.assertEqual(
            "\nBye!\n",
            self.captured_output.getvalue()
        )


class TestBalancePage(TestPage):
    def test_page(self):
        self.balance_page = BalancePage(0)
        self.balance_page.display()
        self.assertEqual(
            "\nBalance: 0\n",
            self.captured_output.getvalue()
        )


class TestLogOutPage(TestPage):
    def test_page(self):
        self.log_out_page = LogOutPage()
        self.log_out_page.display()
        self.assertEqual(
            "\nYou have successfully logged out!\n",
            self.captured_output.getvalue()
        )


if __name__ == '__main__':
    unittest.main()
