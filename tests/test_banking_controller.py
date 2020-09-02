import _context
import unittest
from unittest.mock import MagicMock, patch
from banking.banking_controller import PageController, MenuController, LoggingController, \
    LoggedInController
from banking.banking_model import Card
from banking.banking_view import AccountCreatedPage, CardNumberPage, ExitPage


class TestMenuController(unittest.TestCase):
    @patch('banking.banking_view.MenuPage')
    @patch('banking.banking_model.CardDataBase')
    def setUp(self, mock_menu_page, mock_card_data_base):
        self.mock_menu_page = mock_menu_page
        self.mock_card_data_base = mock_card_data_base
        self.menu_controller = MenuController(self.mock_menu_page, self.mock_card_data_base)

    def test_active_page(self):
        self.assertIs(self.menu_controller.get_page(), self.mock_menu_page)

    def test_create_account(self):
        self.mock_menu_page.get_input = MagicMock(return_value=1)

    def test_log_into_account(self):
        self.mock_menu_page.get_input = MagicMock(return_value=2)

        output_controller = self.menu_controller.activate()

        self.assertIsInstance(output_controller, PageController)
        self.assertIsInstance(output_controller, LoggingController)


    def test_exit_page(self):
        self.mock_menu_page.get_input = MagicMock(return_value=0)

        output_controller = self.menu_controller.activate()

        self.assertIsInstance(output_controller, PageController)


class TestLoggingController(unittest.TestCase):
    @patch('banking.banking_view.CardNumberPage')
    @patch('banking.banking_view.PinPage')
    @patch('banking.banking_model.Logger')
    def setUp(self, mock_card_number_page, mock_card_pin_pag0e, mock_logger):
        self.mock_card_number_page = mock_card_number_page
        self.mock_card_pin_page = mock_card_pin_page
        self.mock_logger = mock_logger
        self.logging_controller = LoggingController(mock_card_number_page, mock_card_pin_page, mock_logger)

    def test_active_page(self):
        self.assertIs(self.logging_controller.get_page(), self.mock_card_number_page)

    def test_logging_wrong_number(self):
        self.mock_logger.is_valid_card_number = MagicMock(return_value=False)
        output_controller = self.logging_controller.activate()
        self.assertIs(self.logging_controller.get_page(), self.mock_card_number_page)
        self.assertIsInstance(output_controller, PageController)
        self.assertIsInstance(output_controller, LoggingController)

    def test_logging_right_number_wrong_pin(self):
        self.mock_card_number_page.get_input = MagicMock(return_value=1111_1111_1111_1111)
        self.mock_logger.is_valid_card_number = MagicMock(return_value=True)
        output_controller = self.logging_controller.activate()
        self.assertIs(self.logging_controller.get_page(), self.mock_card_pin_page)
        self.assertEqual(1111_1111_1111_1111, self.logging_controller.card_number)
        self.assertIsInstance(output_controller, PageController)
        self.assertIsInstance(output_controller, LoggingController)

        self.mock_card_pin_page.get_input = MagicMock(return_value=4000)
        self.mock_logger.log_to = MagicMock(side_effect=ValueError)
        output_controller = self.logging_controller.activate()
        self.assertEqual(4000, self.logging_controller.card_pin)
        self.assertIsInstance(output_controller, PageController)
        self.assertIsInstance(output_controller, LoggingController)

    def test_logging_right_number_right_pin(self):
        self.mock_card_number_page.get_input = MagicMock(return_value=1111_1111_1111_1111)
        self.mock_logger.is_valid_card_number = MagicMock(return_value=True)
        output_controller = self.logging_controller.activate()
        self.assertIs(self.logging_controller.get_page(), self.mock_card_pin_page)
        self.assertEqual(1111_1111_1111_1111, self.logging_controller.card_number)
        self.assertIsInstance(output_controller, PageController)
        self.assertIsInstance(output_controller, LoggingController)

        self.mock_card_pin_page.get_input = MagicMock(return_value=4000)
        output_controller = self.logging_controller.activate()
        self.assertEqual(4000, self.logging_controller.card_pin)
        self.assertIsInstance(output_controller, PageController)
        self.assertIsInstance(output_controller, LoggedInController)


class TestLoggedInController(unittest.TestCase):
    @patch('banking.banking_view.LoggedInPage')
    @patch('banking.banking_model.Account')
    def setUp(self, mock_logged_in_page, mock_account):
        self.mock_logged_in_page = mock_logged_in_page
        self.mock_account = mock_account
        self.logged_in_controller = LoggedInController(mock_logged_in_page, mock_account)

    def test_get_balance(self):
        self.mock_logged_in_page.get_input = MagicMock(return_value=1)
        output_controller = self.logged_in_controller.activate()
        self.assertIsInstance(output_controller, PageController)
        self.assertIsInstance(output_controller, LoggedInController)

    def test_log_out(self):
        self.mock_logged_in_page.get_input = MagicMock(return_value=2)
        output_controller = self.logged_in_controller.activate()

    def test_exit(self):
        self.mock_logged_in_page.get_input = MagicMock(return_value=0)
        output_controller = self.logged_in_controller.activate()
        self.assertIsInstance(output_controller, PageController)


if __name__ == '__main__':
    unittest.main()
