import telebot
from telebot import types
import time
import logging

TOKEN = <ACCESS_TOKEN>
bot = telebot.TeleBot(TOKEN)

logging.basicConfig(level="DEBUG")


@bot.message_handler(commands=['go_kurit'])
def start_poll(message):
    poll = bot.send_poll(
        message.chat.id,
        'Го курить?',
        options=['Го', 'Не го', 'Подождать 5 минут'],
        is_anonymous=False,
        open_period=300
    )

    logging.info(poll)

    bot.poll_data = [message.chat.id, poll.id]
    bot.active_time = int(round(time.time()))
    logging.info(message.chat.id)


# @bot.poll_handler(func=lambda poll: True)
# def process_poll(poll):
#     logging.info('data:')
#     logging.info(poll.correct_option_id)
#     if poll.is_closed:
#
#         bot.send_message(bot.poll_data[0], "Голосование окончено")


@bot.poll_answer_handler(func=lambda poll: True)
def answer_handler(poll):
    if bot.poll_data:
        logging.info(poll.poll_id)
        logging.info(poll.user)
        logging.info(poll.option_ids)
        logging.info("poll_data")
        bot.poll_data.append(poll.user.id)
        logging.info(bot.poll_data)
        end_time = bot.active_time + 10
        count_yes = 0
        count_no = 0
        if poll.option_ids == [0]:
            count_yes += 1

        if poll.option_ids == [1]:
            count_no += 1

        if poll.option_ids == [2]:
            bot.send_message(bot.poll_data[0], f"{poll.user.first_name} просит подождать. Ждём?")
            bot.stop_poll(bot.poll_data[0], bot.poll_data[1])
            wait_poll = bot.send_poll(
                bot.poll_data[0],
                'Ждём?',
                options=['Ждём', 'Не ждём'],
                is_anonymous=False,
                open_period=150
            )
            bot.wait_poll_data = [bot.poll_data[0], wait_poll.id]
            bot.poll_data = None

            del poll

        elif bot.active_time <= end_time:
            bot.stop_poll(bot.poll_data[0], bot.poll_data[1])
            if count_no < count_yes:
                bot.send_message(bot.wait_poll_data[0], "5 минут прошло... Большинство за то, чтобы пойти покурить")
            else:
                bot.send_message(bot.wait_poll_data[0], "5 минут прошло... Большинство против того, чтобы пойти покурить")
            del bot.wait_poll_data
            del poll

        elif len(bot.poll_data) - 2 == bot.get_chat_members_count(bot.poll_data[0]) - 1:
            bot.stop_poll(bot.poll_data[0], bot.poll_data[1])
            if count_no < count_yes:
                bot.send_message(bot.poll_data[0], "Большинство за то, чтобы пойти покурить")
            else:
                bot.send_message(bot.poll_data[0], "Большинство против того, чтобы пойти покурить")
            del bot.wait_poll_data
            del poll

    else:
        logging.info(poll.poll_id)
        logging.info(poll.user)
        logging.info(poll.option_ids)
        logging.info("poll_data")
        bot.wait_poll_data.append(poll.user.id)
        count_yes = 0
        count_no = 0
        if poll.option_ids == [0]:
            count_yes += 1

        if poll.option_ids == [1]:
            count_no += 1

        if len(bot.wait_poll_data) - 2 == bot.get_chat_members_count(bot.wait_poll_data[0]) - 1:
            bot.stop_poll(bot.wait_poll_data[0], bot.wait_poll_data[1])
            if count_no < count_yes:
                bot.send_message(bot.wait_poll_data[0], "Не ждём")
            else:
                bot.send_message(bot.wait_poll_data[0], "Ждём")
            del bot.wait_poll_data
            del poll


if __name__ == "__main__":
    bot.poll_data = []
    bot.wait_poll_data = []
    bot.active_time = time.time()

    bot.polling(none_stop=True)
