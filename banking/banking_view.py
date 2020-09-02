class Displayer:
    def display(self, message):
        print(message)


class Retriever:
    def __init__(self, ask_function):
        self.ask_function = ask_function

    def retrieve(self, question):
        return self.ask_function(question)