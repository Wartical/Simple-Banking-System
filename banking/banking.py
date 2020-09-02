from banking.banking_controller import MainMenuController, LoggedInController
from banking.banking_view import Displayer, Retriever
from banking.banking_model import CardFactory, CardDataBaseSqlite3, Logger


if __name__ == '__main__':
    displayer = Displayer()
    retriever = Retriever(input)
    card_data_base = CardDataBaseSqlite3()

    logger = Logger(card_data_base)
    card_factory = CardFactory(card_data_base)

    main_menu = MainMenuController(displayer, retriever, card_factory, logger)
    keep_going = True
    while keep_going:
        logged_in_card = main_menu.main_loop()
        if main_menu.is_over:
            keep_going = False
            break

        logged_in_menu = LoggedInController(displayer, retriever, logged_in_card, card_data_base, card_factory)
        logged_in_menu.main_loop()
        if logged_in_menu.is_over:
            keep_going = False
            break


