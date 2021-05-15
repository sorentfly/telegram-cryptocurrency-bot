# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

# Use a breakpoint in the code line below to debug your script.
# Press ⌘F8 to toggle the breakpoint.

# ---------------------------------------------------------------------------------------
"""
 Settings in BotFather:
   list of commands:
       start - Приветственное сообщение
       help - Список доступных команд
       price [cryptocurrency] [currency] - Выводит стоимость криптовалюты [cryptocurrency] в эквиваленте на [currency]
"""
# ---------------------------------------------------------------------------------------

# Libs
import os

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler
from pycoingecko import CoinGeckoAPI

import random
import decimal

# Global func
load_dotenv()
cg = CoinGeckoAPI()

# Consts
token = os.environ.get('TOKEN')


# Functions
def start_function(bot, update):
    user = bot.message.from_user
    text = ('Ну, привет, {}. ' \
            '\nДай угадать: опять хочешь узнать цену какой-нибудь крипты?' \
            '\nЕсли что не ясно, пиши /help и я помогу :)').format(user['first_name'])
    bot.message.reply_text(text)


def help_function(bot, update):
    text = 'Короче, тут такое дело: мой создатель - человек недалёкий и пока реализовал только такие команды: ' \
           '\n/start: Показывает приветственное сообщение' \
           '\n/help: Показывает это сообщение' \
           '\n/price: Отображает цену случайной крипты' \
           '\n/price YTN\\YENTEN: Отображает цену конкретной крипты' \
           '\n/price YTN\\YENTEN RUB\\CAD: Отображает цену конкретной крипты в указанной валюте' \
           '\nВот и всё, лол)'
    bot.message.reply_text(text)


def get_price_function(bot, context):
    coins = cg.get_coins_list()
    currency_param = 'usd'

    def get_coin_by_id(coin_id):
        return cg.get_coin_by_id(coin_id,
                                 localization=False,
                                 tickers=False,
                                 market_data=True,
                                 community_data=False,
                                 developer_data=False,
                                 sparkline=False)

    def get_random_coin():
        """

        :return: random coin obj
        """

        def get_coins_ids(_coin):
            return _coin['id']

        coins_ids = list(map(get_coins_ids, coins))
        random_coin_id = random.choice(coins_ids)
        random_coin = get_coin_by_id(random_coin_id)
        return random_coin

    def get_coin_by_param(param):
        param = param.lower()
        coin_by_param = list(filter(
            lambda x: x['symbol'].lower() == param or x['name'].lower() == param, coins)
        )
        if len(coin_by_param) == 0:
            return None

        coin_id_by_param = coin_by_param[0]['id']
        return get_coin_by_id(coin_id_by_param)

    user = bot.message.from_user
    if len(context.args) == 0:
        # In case no args given => return random coin
        try:
            coin = get_random_coin()
        except BaseException:
            bot.message.reply_text('π🚪асы из CoinGecko развыёбывались, типа дохуя запросов идёт, прикинь?' \
                                   '\nКороче погодь и всё будет чётко.')
            return
        coin_price = coin['market_data']['current_price'][currency_param]  # bitcoin has 8 nums after dot
        # coin_price = decimal.Decimal(coin_price)
        decimal.getcontext().prec = 8
        coin_price = decimal.getcontext().create_decimal(coin_price)
        text = 'Уважаемый {}, я должен сам придумать какую крипту вывести?' \
               '\nОкей! Пусть это будет {}:\n{} стоит {} {}'.format(user['first_name'],
                                                                    coin['name'],
                                                                    coin['symbol'].upper(),
                                                                    coin_price,
                                                                    currency_param.upper())
        bot.message.reply_text(text)
        return

    coin_param = context.args[0]
    if len(context.args) == 2:
        currency_param = context.args[1].lower()
    try:
        coin = get_coin_by_param(coin_param)
        if coin is None:
            bot.message.reply_text(f'Скажи, ты уверен, что {coin_param} реально существует? Я не нашёл...')
            return
    except BaseException:
        bot.message.reply_text('π🚪асы из CoinGecko развыёбывались, типа дохуя запросов идёт, прикинь?' \
                               '\nКороче погодь и всё будет чётко.')
        return

    try:
        coin_price = coin['market_data']['current_price'][currency_param]
    except BaseException:
        bot.message.reply_text(f'Не думаю, что {currency_param} применим к коину {coin_param}, я отображу в USD')
        currency_param = 'usd'
    coin_price = coin['market_data']['current_price'][currency_param]
    # coin_price = decimal.Decimal(coin_price)
    decimal.getcontext().prec = 8
    coin_price = decimal.getcontext().create_decimal(coin_price)
    text = f'Коин {coin["name"]}:\n{coin["symbol"].upper()} стоит {coin_price} {currency_param.upper()}'
    bot.message.reply_text(text)
    return


def main():
    updater = Updater(token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start_function))
    dp.add_handler(CommandHandler('help', help_function))
    dp.add_handler(CommandHandler('price', get_price_function, pass_args=True))

    updater.start_polling()
    updater.idle()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
