import telebot
import json
from telebot import types
import threading
import schedule
import time

token = '7162546131:AAE3mTOo4U9jRBJcSIPbJOvwOGyBvujkLHM'
user = ["hvru", 718189301]

bot = telebot.TeleBot(token)

tasks = {
    'pickup': False,
    'sadhu': False,
    'cold shower': False,
    'lku at 12:00': False,
    'lku at 15:00': False,
    'lku at 18:00': False
}

habit_emojis = {
    "pickup": "🙆‍♂️",
    "sadhu": "🧘‍♂️",
    "cold shower": "🚿",
    "lku at 12:00": "🕛",
    "lku at 15:00": "🕒",
    "lku at 18:00": "🕕"
}

def modify_habit_data(task_name, update_func):
    with open('data.json', 'r') as file:
        data = json.load(file)
    for habit in data['habits']:
        if habit['name'] == task_name:
            update_func(habit)
            break
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

def update_maxstreak(task_name):
    def update(habit):
        if habit['current_streak'] > habit['max_streak']:
            habit['max_streak'] = habit['current_streak']
    modify_habit_data(task_name, update)

def reset_streak(task_name):
    def update(habit):
        if tasks[task_name] == False:
            habit['current_streak'] = 0
    modify_habit_data(task_name, update)

def increment_streak(task_name):
    def update(habit):
        habit['total_count'] += 1
        habit['current_streak'] += 1
    modify_habit_data(task_name, update)

def reset_daily_tasks():
    global tasks
    for task_name in tasks:
        reset_streak(task_name)
        tasks[task_name] = False
    bot.send_message(user[1], "Ежедневные задания обновились!")


def lku_notification():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
        types.KeyboardButton("Seiday")
    )
    bot.send_message(user[1], "Время выполнить комплекс упражнений!\n\nПоднятия на носки: 30 раз\nПриседания: 15 раз\nУпражнение Кегеля: 100 раз", reply_markup=keyboard)

def schedule_task():
    schedule.every().day.at("00:00", "Asia/Almaty").do(reset_daily_tasks)
    times = ["12:00", "15:00", "18:00"]
    for time in times:
        schedule.every().day.at(time, "Asia/Almaty").do(lku_notification)

def poll_bot():
    while True:
        bot.infinity_polling()

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

main_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
    types.KeyboardButton("Seiday"),
    types.KeyboardButton("Soloway"),
    types.KeyboardButton("Halt")
)

@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.id == user[1]:
        bot.send_message(message.chat.id, "Ave. 🕊️\n\nAvenue - твой соловей против течения.\n\nВ этом чате я твой лучший друг, спутник, и единственный, кто по-настоящему верит в тебя! ☺️", reply_markup=main_keyboard)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к использованию бота.")

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.chat.id == user[1]:
        if message.text.lower() == "halt":
            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
            types.KeyboardButton("Seiday"),
            types.KeyboardButton("Soloway")
            )
            bot.send_message(message.chat.id, "Ave. 🕊️\n\nAvenue - твой соловей против течения.\n\nТы начал этот путь 13.04.2024 📆\nИ я хочу видеть твой результат через год!\n\nВ этом чате я твой лучший друг, спутник, и единственный, кто по-настоящему верит в тебя! ☺️", reply_markup=keyboard)

        elif message.text.lower() == "seiday":
            active_tasks = [f"{task_name}" for task_name, done in tasks.items() if not done]
            done_tasks = [f"{habit_emojis.get(task_name.lower(), '')} {task_name.capitalize()}" for task_name, done in tasks.items() if done]


            keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            buttons = [types.KeyboardButton(task_name.capitalize()) for task_name in active_tasks]
            buttons.append(types.KeyboardButton("Halt"))
            keyboard.add(*buttons)

            pattern = "Отлично! ☺️\n\nВсе задания выполнены!"
            main_message = 'Еще один день соловей! ☀️🕊️\n\n' if active_tasks else pattern
            if main_message == pattern:
                done_tasks_message = ''
            elif done_tasks:
                done_tasks_message = 'Выполненные задания:\n' + '\n'.join(done_tasks)
            else:
                done_tasks_message = "Выполненных заданий еще нет. ⌛"

            bot.send_message(
                message.chat.id,
                f"{main_message}{done_tasks_message}",
                reply_markup=keyboard
            )

        elif message.text.lower() in tasks.keys():
            task_name = message.text.lower()

            for task_name_dict, done in tasks.items():
                if task_name_dict.lower() == task_name and done:
                    bot.send_message(message.chat.id, "Задание уже выполнено. 🤨", reply_markup=main_keyboard)
                    return

            bot.send_message(user[1], f"{task_name.capitalize()} выполнено. 🙌\n\nСтатистика обновлена! 🕊️", reply_markup=main_keyboard)

            increment_streak(task_name)
            update_maxstreak(task_name)

            for task_name_dict in tasks.keys():
                if task_name_dict.lower() == message.text.lower():
                    tasks[task_name] = True
                    break

        elif message.text.lower() == "soloway":
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                types.KeyboardButton("Halt")
            )
            with open('data.json', 'r') as file:
                data = json.load(file)
            stat_message = "Soloway 🕊️:\n\nТвоя подробная статистика 📊\n\nИ запомни, важен не стрик,\nважна непрерывность. ➰\n\n"
            for habit in data['habits']:
                emoji = habit_emojis.get(habit['name'].lower(), "❓")
                stat_message += f"____{emoji} {habit['name'].capitalize()} {emoji}:____\n"
                stat_message += f"🌀 Общее количество: {habit['total_count']},\n"
                stat_message += f"☄️ Максимальный стрик: {habit['max_streak']},\n"
                stat_message += f"🔥 Текущий стрик: {habit['current_streak']}\n\n"
            bot.send_message(message.chat.id, stat_message, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к использованию бота.")

if __name__ == '__main__':
    bot.send_message(user[1], "Внимание! Бот был перезапущен! 🤔")

    schedule_task_thread = threading.Thread(target=schedule_task)
    schedule_task_thread.start()

    bot_thread = threading.Thread(target=poll_bot)
    bot_thread.start()

    run_schedule()
