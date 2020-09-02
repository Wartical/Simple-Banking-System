import unittest
import _context
from unittest.mock import patch, MagicMock
from banking.banking_model import Card, CardDataBase, CardFactory\
    , Account, Logger, CardDataBaseSqlite3


class TestAccount(unittest.TestCase):

    def setUp(self):
        self.account = Account()

    def test_account_initialisation(self):
        self.assertIsInstance(self.account, Account)
        self.assertEqual(0, self.account.balance)

    def test_deposit(self):
        self.account.deposit(10)
        self.assertEqual(10, self.account.balance)

        self.account.deposit(18)
        self.assertEqual(28, self.account.balance)

        with self.assertRaises(ValueError):
            self.account.deposit(-10)

        self.assertEqual(28, self.account.balance)

    def test_withdraw(self):
        self.account.deposit(10)
        self.account.withdraw(10)
        self.assertEqual(0, self.account.balance)

        self.account.deposit(19)
        self.account.withdraw(7)
        self.assertEqual(12, self.account.balance)

        with self.assertRaises(ValueError):
            self.account.withdraw(-10)
        self.assertEqual(12, self.account.balance)

        with self.assertRaises(ValueError):
            self.account.withdraw(13)
        self.assertEqual(12, self.account.balance)

    def test_rounding(self):
        self.account.deposit(12.150253132)
        self.assertEqual(12.15, self.account.balance)
        self.account.withdraw(self.account.balance)
        self.assertEqual(0, self.account.balance)

        self.account.deposit(0.136)
        self.account.withdraw(0.14)
        self.assertEqual(0, self.account.balance)


class TestCard(unittest.TestCase):
    def test_card(self):
        self.card = Card(0, 24)
        self.assertEqual(0, self.card.number)
        self.assertEqual(24, self.card.pin)

        self.card = Card(4000_0015_7869_2485, 8641)

        self.assertEqual(400_000, self.card.get_issuer_identification_number())
        self.assertEqual(157869248, self.card.get_customer_account_number())
        self.assertEqual(5, self.card.get_checksum())
        self.assertEqual(8641, self.card.pin)


class TestCardFactory(unittest.TestCase):
    def setUp(self):
        card_data_base = CardDataBase()
        card_data_base.get_last_emitted_card = MagicMock(return_value=Card(4000_0000_0000_0000, 0000))
        card_data_base.add_card = MagicMock(return_value=None)
        self.card_factory = CardFactory(card_data_base)

    def test_pin_number(self):
        for i in range(10_000):
            card = self.card_factory.new_card()
            self.assertGreaterEqual(9999, card.pin)
            self.assertLessEqual(0000, card.pin)

            self.assertEqual('400000', str(card.number)[:6])
            self.assertEqual(16, len(str(card.number)))

    def test_luhn_algorithm(self):
        self.assertEqual(3, self.card_factory.compute_check_sum(400000, 844943340))
        self.assertEqual(6, self.card_factory.compute_check_sum(400000, 493832089))

    def test_is_valid(self):
        self.assertTrue(self.card_factory.is_valid(4000_0084_4943_3403))
        self.assertFalse(self.card_factory.is_valid(4010_0084_4943_3403))
        self.assertFalse(self.card_factory.is_valid(4000_0084_4943_3404))

        self.assertTrue(self.card_factory.is_valid(4000_0049_3832_0896))
        self.assertFalse(self.card_factory.is_valid(4010_00849_3832_0896))
        self.assertFalse(self.card_factory.is_valid(4000_0049_3832_0897))


class TestCardDataBase(unittest.TestCase):
    def setUp(self):
        self.card_data_base = CardDataBase()

    def test_last_emitted_card(self):
        card = self.card_data_base.get_last_emitted_card()
        self.assertEqual(4000_0000_0000_0000, card.number)

    def test_add_card(self):
        card1 = Card(1, 2)
        self.card_data_base.add_card(card1)
        self.assertEqual(card1.number, self.card_data_base.get_last_emitted_card().number)
        self.assertEqual(card1.pin, self.card_data_base.get_last_emitted_card().pin)

    def test_is_card(self):
        card1 = Card(1, 2)
        self.card_data_base.add_card(card1)
        self.assertTrue(self.card_data_base.is_card(card1))
        card2 = Card(3, 4)
        self.assertFalse(self.card_data_base.is_card(card2))

        self.card_data_base.add_card(card2)
        self.assertTrue(self.card_data_base.is_card(card2))

        self.assertTrue(self.card_data_base.is_card(card1))

    def test_get_card(self):
        card1 = Card(1, 2)
        card2 = Card(3, 4)
        self.card_data_base.add_card(card1)
        self.card_data_base.add_card(card2)

        self.assertIs(card1, self.card_data_base.get_card(1))
        self.assertIs(card2, self.card_data_base.get_card(3))

        with self.assertRaises(ValueError):
            self.card_data_base.get_card(2)


class TestCardDataBaseSqlite3(unittest.TestCase):
    @patch('banking.banking_model.Card')
    def setUp(self, mock_card):
        self.card_data_base = CardDataBaseSqlite3()
        self.mock_card = mock_card
        self.mock_card.number = 4000_0011_1111_1112
        self.mock_card.pin = 0000
        self.mock_card.account.balance = 10
        self.card_data_base.add_card(self.mock_card)

    @patch('banking.banking_model.Card')
    def tearDown(self, mock_card):
        self.card_data_base.remove_card(self.mock_card)

    def test_get_card(self):
        number = 4000_0011_1111_1112
        self.assertEqual(self.card_data_base.get_card(number).number, self.mock_card.number)
        self.assertEqual(self.card_data_base.get_card(number).pin, self.mock_card.pin)
        self.assertEqual(self.card_data_base.get_card(number).account.balance, self.mock_card.account.balance)

    def test_get_last_emitted_card(self):
        for num in range(1, 100):
            self.mock_card.number = int('400000'+str(num).zfill(10))
            self.mock_card.pin = int(str(num).zfill(4))
            self.mock_card.account.balance = 0
            self.card_data_base.add_card(self.mock_card)
            self.assertEqual(self.card_data_base.get_last_emitted_card().number, int(self.mock_card.number))
            self.assertEqual(self.card_data_base.get_last_emitted_card().pin, int(self.mock_card.pin))

    def test_update_card(self):
        initial_balance = self.card_data_base.get_card(self.mock_card.number).account.balance
        self.mock_card.account.balance = initial_balance + 10
        self.card_data_base.update_card(self.mock_card)
        final_balance =  self.card_data_base.get_card(self.mock_card.number).account.balance

        self.assertEqual(initial_balance, final_balance - 10)


class TestLogIn(unittest.TestCase):
    @patch('banking.banking_model.CardDataBase')
    def setUp(self, MockCardDataBase):
        self.mock_card_data_base = MockCardDataBase
        self.mock_card_data_base.get_card = MagicMock(return_value=Card(4000_0011_1111_1112, 0000))
        self.logger = Logger(self.mock_card_data_base)

    def test_log_in(self):
        card_number = 4000_0011_1111_1112
        pin = 0000
        card = self.logger.log_to(card_number, pin)
        self.assertIsInstance(card, Card)

        with self.assertRaises(ValueError):
            card_number = 4000_0011_1111_1112
            pin = 1
            self.logger.log_to(card_number, pin)

    def test_is_valid_card_number(self):
        number = 4000_0011_1111_1112
        self.assertTrue(self.logger.is_valid_card_number(number))

        number = 4000_0111_1111_1112
        self.assertFalse(self.logger.is_valid_card_number(number))

        number = 4000_0011_1111_111
        self.assertFalse(self.logger.is_valid_card_number(number))

        number = 40000_0011_1111_11122
        self.assertFalse(self.logger.is_valid_card_number(number))


if __name__ == '__main__':
    unittest.main()
