import unittest
import _context
import sys
from io import StringIO
from banking.banking_view import Displayer, Retriever


class TestPage(unittest.TestCase):
    def setUp(self):
        self.captured_output = StringIO()
        self.old_stdout = sys.stdout
        sys.stdout = self.captured_output  # redirect stdout

    def tearDown(self):
        sys.stdout = self.old_stdout


class TestDisplayer(TestPage):
    def test_display(self):
        self.displayer = Displayer()
        for message in ['hello', '\nThis is over\n', '1\n2\n3\n4']:
            self.displayer.display(message)
            self.assertEqual(message + '\n', self.captured_output.getvalue())
            self.captured_output.__init__()


class TestRetriever(TestPage):
    def test_retrieve(self):
        def get_input(message):
            print(message)
            return 'Bob'
        self.retriever = Retriever(get_input)

        for question in ['What\'s your name?', 'How much?\n', '1?\n2?\n3?\n4?']:
            answer = self.retriever.retrieve( question)
            self.assertEqual(question + '\n', self.captured_output.getvalue())
            self.assertEqual('Bob', answer)
            self.captured_output.__init__()


if __name__ == '__main__':
    unittest.main()
