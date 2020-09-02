import _context
import unittest
import sys
from io import StringIO
from unittest.mock import MagicMock, patch, Mock
from banking.banking_controller import Controller, MainMenuController, LoggedInController
from banking.banking_model import Card
from banking.banking_view import Displayer, Retriever



class MockDisplayer(Displayer):
    def display(self, message):
        print(message)


class MockRetriever(Retriever):
    def __init__(self, ask_function):
        self.ask_function = ask_function

    def retrieve(self, message):
        return self.ask_function(message)


class TestPage(unittest.TestCase):
    def setUp(self):
        self.captured_output = StringIO()
        self.old_stdout = sys.stdout
        sys.stdout = self.captured_output  # redirect stdout

        def get_input(message):
            global USER_INPUT
            print(message)
            return USER_INPUT

        self.mock_displayer = MockDisplayer()
        self.mock_retriever = MockRetriever(get_input)

    def tearDown(self):
        sys.stdout = self.old_stdout


class TestMainMenuController(TestPage):
    @patch('banking.banking_model.CardFactory')
    @patch('banking.banking_model.Logger')
    def setUp(self, mock_card_factory, mock_logger):
        super().setUp()

        self.mock_card_factory = mock_card_factory
        self.mock_logger = mock_logger
        self.main_menu_controller = MainMenuController(
            self.mock_displayer,
            self.mock_retriever,
            self.mock_card_factory,
            self.mock_logger
        )

    def test_show_possible_choices(self):
        global USER_INPUT
        USER_INPUT = '1'
        answer = self.main_menu_controller.witch_choices()
        self.assertEqual(
            "\n1. Create an account\n" +
            "2. Log into account\n" +
            "0. Exit\n", self.captured_output.getvalue())
        self.captured_output.__init__()

        self.assertEqual(USER_INPUT, answer)

    def test_main_loop_exit(self):
        global USER_INPUT
        USER_INPUT = 'Any thing'
        with self.assertRaises(RecursionError):
            self.main_menu_controller.main_loop()
            self.assertFalse(self.main_menu_controller.is_over)

        USER_INPUT = '0'
        self.assertIsNone(self.main_menu_controller.main_loop())
        self.assertTrue(self.main_menu_controller.is_over)
        self.assertTrue(
            "Bye!"
            in self.captured_output.getvalue()
        )
        self.captured_output.__init__()

    def test_main_loop_create_account(self):
        self.captured_output.__init__()
        global USER_INPUT
        USER_INPUT = '1'

        with self.assertRaises(RecursionError):
            card = Mock()
            card.number = 4000_0011_1111_1112
            card.pin = 5555
            self.mock_card_factory.new_card = MagicMock(return_value=card)
            self.main_menu_controller.main_loop()

        self.assertTrue(
            f"\nYour card have been created\n" +
            f"Your card number:\n" +
            f"{card.number}\n" +
            f"Your card PIN:\n" +
            f"{card.pin}"
            in self.captured_output.getvalue()
        )
        self.captured_output.__init__()

    def test_main_loop_wrong_connect_to_account(self):
        self.captured_output.__init__()

        global USER_INPUT
        USER_INPUT = '2'

        card = Mock()
        card.number = 40000_0011_1111_1112
        card.pin = 5555

        self.mock_logger.log_to = MagicMock(return_value=card, side_effect=ValueError)

        with self.assertRaises(RecursionError):
            self.main_menu_controller.main_loop()

        self.assertTrue(
            f"\nEnter your card number:"
            in self.captured_output.getvalue()
        )
        self.assertTrue(
            f"\nEnter your PIN:"
            in self.captured_output.getvalue()
        )

        self.assertFalse(
            "\nYou have successfully logged in!"
            in self.captured_output.getvalue()
        )

        self.assertTrue(
            f"\nWrong card number or PIN!\n"
            in self.captured_output.getvalue()
        )
        self.captured_output.__init__()

    def test_main_loop_right_connect_to_account(self):
        self.captured_output.__init__()

        global USER_INPUT
        USER_INPUT = '2'

        card = Mock()
        card.number = 40000_0011_1111_1112
        card.pin = 5555

        self.mock_logger.log_to = MagicMock(return_value=card)
        return_card = self.main_menu_controller.main_loop()
        self.assertTrue(
            f"\nEnter your card number:"
            in self.captured_output.getvalue()
        )
        self.assertTrue(
            f"\nEnter your PIN:"
            in self.captured_output.getvalue()
        )

        self.assertTrue(
            f"\nYou have successfully logged in!"
            in self.captured_output.getvalue()
        )

        self.assertIs(card, return_card)
        self.captured_output.__init__()


class TestLoggedInController(TestPage):
    @patch('banking.banking_model.CardDataBaseSqlite3')
    @patch('banking.banking_model.CardFactory')
    def setUp(self, mock_card_data_base, mock_card_factory):
        super().setUp()
        self.mock_card_data_base = mock_card_data_base
        self.mock_card_factory = mock_card_factory
        self.mock_card = Mock()
        self.mock_card.number = 4000_0011_1111_1111_1112
        self.mock_card.pin = 5555
        self.mock_card.account.balance = 99
        self.logged_in_controller = LoggedInController(
            self.mock_displayer,
            self.mock_retriever,
            self.mock_card,
            self.mock_card_data_base,
            mock_card_factory)

    def test_show_possible_choices(self):
        global USER_INPUT
        USER_INPUT = '1'
        answer = self.logged_in_controller.witch_choices()
        self.assertEqual(
            "\n1. Balance\n" +
            "2. Add income\n" +
            "3. Do transfer\n" +
            "4. Close account\n" +
            "5. Log out\n" +
            "0. Exit\n", self.captured_output.getvalue())
        self.captured_output.__init__()

        self.assertEqual(USER_INPUT, answer)

    def test_main_loop_exit(self):
        global USER_INPUT
        USER_INPUT = 'Any thing'
        with self.assertRaises(RecursionError):
            self.assertIsNone(self.logged_in_controller.main_loop())
            self.assertFalse(self.logged_in_controller.is_over)

        USER_INPUT = '0'
        self.logged_in_controller.main_loop()
        self.assertTrue(self.logged_in_controller.is_over)
        self.assertTrue(
            "Bye!"
            in self.captured_output.getvalue()
        )
        self.captured_output.__init__()

    def test_main_loop_log_out(self):
        global USER_INPUT
        USER_INPUT = '5'
        self.assertIsNone(self.logged_in_controller.main_loop())
        self.assertFalse(self.logged_in_controller.is_over)
        self.assertTrue(
            "\nYou have successfully logged out!"
            in self.captured_output.getvalue()
        )
        self.captured_output.__init__()

    def test_main_loop_get_balance(self):
        global USER_INPUT
        USER_INPUT = 'AnyThing'
        with self.assertRaises(RecursionError):
            self.logged_in_controller.main_loop()

        self.assertTrue(
            "\nBalance: 99"
            not in self.captured_output.getvalue()
        )
        self.captured_output.__init__()

        USER_INPUT = '1'
        with self.assertRaises(RecursionError):
            self.logged_in_controller.main_loop()

        self.assertTrue(
            "\nBalance: 99"
            in self.captured_output.getvalue()
        )

    def test_main_loop_enter_income(self):
        global USER_INPUT
        USER_INPUT = 'AnyThing'
        with self.assertRaises(RecursionError):
            self.logged_in_controller.main_loop()

        self.assertTrue(
            "\nEnter income:"
            not in self.captured_output.getvalue()
        )
        self.captured_output.__init__()

        USER_INPUT = '2'
        with self.assertRaises(RecursionError):
            self.logged_in_controller.main_loop()

        self.assertTrue(
            "\nEnter income:"
            in self.captured_output.getvalue()
        )

        self.assertTrue(
            "Income was added!"
            in self.captured_output.getvalue()
        )

        self.captured_output.__init__()

    def test_main_loop_transfer_money_invalid_number(self):
        global USER_INPUT
        USER_INPUT = '3'
        self.mock_card_factory.is_valid = MagicMock(return_value=False)
        with self.assertRaises(RecursionError):
            self.logged_in_controller.main_loop()

        self.assertTrue(
            "\nTransfer\n" +
            "Enter card number:"
            in self.captured_output.getvalue()
        )

        self.assertTrue(
            "Probably you made a mistake in the card number. Please try again!"
            in self.captured_output.getvalue()
        )

    def test_main_loop_transfer_money_no_card(self):
        global USER_INPUT
        USER_INPUT = '3'
        self.mock_card_factory.is_valid = MagicMock(return_value=True)
        self.mock_card_data_base.get_card = MagicMock(side_effect=ValueError)
        with self.assertRaises(RecursionError):
            self.logged_in_controller.main_loop()

        self.assertTrue(
            "\nTransfer\n" +
            "Enter card number:"
            in self.captured_output.getvalue()
        )

        self.assertTrue(
            "Such a card does not exist."
            in self.captured_output.getvalue()
        )

    def test_main_transfer_money(self):
        global USER_INPUT
        USER_INPUT = '3'
        self.mock_card_factory.is_valid = MagicMock(return_value=True)
        mock_card_2 = Mock()
        mock_card_2.account.balance = 0
        self.mock_card_data_base.get_card = MagicMock(return_value=mock_card_2)
        with self.assertRaises(RecursionError):
            self.logged_in_controller.main_loop()

        self.assertTrue(
            "\nTransfer\n" +
            "Enter card number:"
            in self.captured_output.getvalue()
        )

        self.assertTrue(
            "Enter how much money you want to transfer:"
            in self.captured_output.getvalue()
        )
        self.assertTrue(
            "Success!"
            in self.captured_output.getvalue()
        )

    def test_main_loop_close_account(self):
        global USER_INPUT
        USER_INPUT = '4'
        self.logged_in_controller.main_loop()
        self.assertTrue(
            "\nThe account has been closed!\n"
            in self.captured_output.getvalue()
        )
        self.assertFalse(self.logged_in_controller.is_over)


if __name__ == '__main__':
    unittest.main()






