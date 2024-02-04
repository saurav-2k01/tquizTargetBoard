import os

from flask import Flask, request, abort
from telebot import *
from hidden_variable import _update_, API_KEY, URL
from waitress import serve
from csvhandler import csv2json
import json
import time
from Result import Answer_Stats
from Data import QuizBotData
from log_collection import logCollection as log


bot = TeleBot(API_KEY, num_threads=100)
bot.delete_webhook()
bot.set_webhook(f"{URL}/webhook", max_connections=100)
logger = log().logger
user_data = {}
quiz_state = {}
active_group = {}
active_polls = {}
submitted_answer = {}
correct_answer_ids = {}
description = {}
collected_data = []
global start_time
global key_id


@bot.message_handler(commands=['start_quiz'])
def greet(message):
    try:
        bot.reply_to(message, "Welcome To Target Board Quiz_Bot")
        bot.send_message(message.chat.id, "Enter Key 🔑")
        bot.register_next_step_handler(message, quiz)
        #print(message)
    except Exception as E:
        logger.debug(E)


@bot.message_handler(commands=['stop'])
def stop_quiz(message):
    quiz_state[message.chat.id] = 0

@bot.message_handler(commands=['help'])
def helps(message):
    text = """I can help you organize and manage quiz.

You can control me by sending these commands:

<b>Organizing Quiz</b>
/newquiz - organize a new quiz.
/skip - skip description of a quiz.
/help - get help.

<b>Start Quiz</b>
/start_quiz - start quiz.
/stop - stop quiz.
/result - show result.

<b>What you will need in order to organize and start quiz.</b>
1. File (csv or excel)
2. Key - you will get after organizing quiz.
"""
    try:
        bot.send_message(message.chat.id, text, parse_mode="html")
    except Exception as E:
        logger.debug(E)

@bot.message_handler(commands=['start_quiz'])
def quiz(message):
    try:
        msg = message.text
        msg_id = message.chat.id
        if (len(msg) == 16) and msg.isupper():
            key = msg
            active_group[msg_id] = key
            quiz_state[msg_id] = 1
            active_polls[msg_id] = {}
            bot.send_message(msg_id, "Key Accepted.")
            data = QuizBotData()
            data = data.get_quiz_table_name(key)
            if data != -1:
                question_data = data['question_data']
                quiz_data = data['quiz_data']
                count = 1
                size = len(question_data)
                description[msg_id] = quiz_data[6]
                bot.send_message(msg_id, f"""
                🎲 Get ready for the quiz *'{quiz_data[6]}*'

🖊 *{size}* question
⏱ *{quiz_data[5]}* seconds per question
🏁 Press the button below when you are ready.
Send /stop to stop it.""", parse_mode='Markdown')
                y = bot.send_message(msg_id, "The quiz will start in *10* seconds.", parse_mode="Markdown")
                bot.delete_message(msg_id, message.id)
                for i in timer():
                    if type(i) == int:
                        bot.edit_message_text(f"The quiz will start in *{i}* seconds.", msg_id, y.id, parse_mode="Markdown")
                    else:
                        bot.edit_message_text(f"*{i}*", msg_id, y.id,parse_mode="Markdown")
                bot.delete_message(msg_id, y.id)


                for i in question_data:
                    try:
                        question = i[3]
                        if (i[8] == "") or (i[8] == None):
                            options = i[4:8]
                        else:
                            options = i[4:9]
                        answer = {
                            "a": 0, "b": 1, "c": 2, "d": 3, "e": 4
                        }
                        answer_id = answer[i[9].lower()]
                        opentime = int(quiz_data[5])
                        global start_time
                        start_time = time.time()
                        x = bot.send_poll(
                            chat_id=message.chat.id,
                            question=f"[{count}/{size}]  {question}",
                            is_anonymous=False,
                            type="quiz",
                            options=options,
                            correct_option_id=answer_id,
                            open_period=opentime
                        )
                        active_polls[msg_id][x.poll.id] = answer_id
                        time.sleep(opentime + 5)
                        count += 1
                        if not quiz_state.get(msg_id):
                            break
                        else:
                            continue
                    except Exception as E:
                        logger.debug(E)
                bot.send_message(msg_id, result(msg_id), parse_mode="html")
            else:
                bot.send_message(message.chat.id, "Key not found.")
    except Exception as E:
        logger.debug(E)

@bot.message_handler(content_types=['document'])
def addfile(message):
    try:
        if user_data['time'] != 0:
            file_name = message.document.file_name
            extension_ = file_name.split(".")[-1]
            if (extension_.lower() == "csv") or extension_.lower() == "xlsx":
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                # print(f"{file_name}File downloaded")
                with open(file_name, 'wb') as new_file:
                    new_file.write(downloaded_file)
                x = QuizBotData()
                try:
                    if extension_.lower() == "csv":
                        key = x.upload_csv(file_name, user_data)
                    else:
                        key = x.upload_excel(file_name, user_data)
                except Exception as E:
                    os.remove(file_name)
                else:
                    if key != -1:
                        text1 = f""" Keep this key for future usage. This will be needed for starting quiz later on."""
                        text2 = f"""Organized by: {user_data['username']}
Time for each question: {user_data['time']}
Key: {key}
Description: {user_data['description']}"""

                        bot.send_message(message.chat.id, text1)
                        bot.send_message(message.chat.id, text2)
                        os.remove(file_name)
                    else:
                        bot.send_message(message.chat.id, "Questions are more than 200.")
            else:
                bot.send_message(message.chat.id, f".{extension_} file is not supported on this bot. Please try again.")
        else:
            get_time(message)
    except Exception as E:
        logger.debug(E)




@bot.message_handler(commands=["newquiz"])
def organize_quiz(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.first_name
        user_data['username'] = username
        user_data['user id'] = user_id
        user_data["description"] = ""
        user_data["time"] = 0
        bot.send_message(user_id, "Enter Description")
        bot.register_next_step_handler(message, get_description)
    except Exception as E:
        logger.debug(E)

def get_description(message):
    try:
        user_id = message.from_user.id
        m = message.text
        if user_data['description'] == "":
            if m.lower() == "/skip":
                user_data['description'] = ''
                bot.send_message(user_id,
                                 "Enter time for Each question, in multiple of 5 seconds, eg. 5, 10, 15, 20, etc.")
                bot.register_next_step_handler(message, get_time)
            else:
                user_data['description'] = m
                bot.send_message(user_id,
                                 "Enter time for Each question, in multiple of 5 seconds, eg. 5, 10, 15, 20, etc.")
                bot.register_next_step_handler(message, get_time)
        else:
            bot.send_message(user_id, "Enter time for Each question, in multiple of 5 seconds, eg. 5, 10, 15, 20, etc.")
            bot.register_next_step_handler(message, get_time)
    except Exception as E:
        logger.debug(E)


def get_time(message):
    try:
        user_id = message.from_user.id
        m = message.text
        if user_data['time'] == 0:
            try:
                if int(m) % 5 == 0:
                    if int(m) < 1001:
                        user_data['time'] = int(m)
                        # print(user_data)
                        bot.send_message(user_id, "upload a csv or excel file.")
                        bot.register_next_step_handler(message, addfile)
                    else:
                        bot.send_message(user_id, "Maximum time is 1000 seconds. Try again. :)")
                        bot.register_next_step_handler(message, get_time)
                else:
                    bot.send_message(user_id, "Enter a  valid number. Try again. :)")
                    bot.register_next_step_handler(message, get_time)
            except:
                bot.send_message(user_id, "Enter a valid Number. Try again. :)")
                bot.register_next_step_handler(message, get_time)
        else:
            # print(user_data)
            bot.send_message(message.chat.id, "upload a csv")
            bot.register_next_step_handler(message, addfile)
    except Exception as E:
        logger.debug(E)




@bot.poll_answer_handler()
def answer(PollAnswer):
    try:
        submission_time = time.time()
        time_taken = submission_time - start_time
        user = PollAnswer.user
        answer = {}
        answer["poll_id"] = PollAnswer.poll_id
        answer['user_id'] = user.id
        answer['username'] = user.username
        answer['firstname'] = user.first_name
        answer['lastname'] = user.last_name
        answer['time_taken'] = time_taken
        answer['option_ids'] = PollAnswer.option_ids
        collected_data.append(answer)
    except Exception as E:
        logger.debug(E)

def create_data_collection(msg_id):
    data = {'collected_data':[],
            'correct_answers_ids':{}
            }
    for poll in active_polls.get(msg_id):
        for p in collected_data:
            if poll == p.get('poll_id'):
                data['collected_data'].append(p)
            else:
                continue
    data['correct_answers_ids'] = active_polls.get(msg_id)
    return data


def result(msg_id):
    try:
        data = create_data_collection(msg_id)
        lb = Answer_Stats(data.get('collected_data'), data.get('correct_answers_ids'))
        lb.generate_leaderboard()
        res = lb.result
        text = []
        detail = f"🏁 The quiz '<b>{description.get(msg_id)}</b>' has finished!"
        count = 1
        limit = 50
        for i in res:
            if count == 1:
                _ = f"{'🥇'} {i.get('fullname')}-<b>{i.get('score')}</b> ({i.get('time_taken')})"
            elif count == 2:
                _ = f"{'🥈'} {i.get('fullname')}-<b>{i.get('score')}</b> ({i.get('time_taken')})"
            elif count == 3:
                _ = f"{'🥉'} {i.get('fullname')}-<b>{i.get('score')}</b> ({i.get('time_taken')})"
            else:
                _ = f"{count} {i.get('fullname')}-<b>{i.get('score')}</b> ({i.get('time_taken')})"
            text.append(_)
            count += 1
            if count > limit:
                break
        text = "\n".join(text)

        if text != "":
            text = detail + "\n" + text + "\n\n" + "🏆 Congratulations to the winners!"
            #bot.send_message(msg_id, result, parse_mode="html")
            return text
        else:
            return "No result to show."
    except Exception as E:
        logger.debug(E)

@bot.message_handler(commands=['result'])
def show_result(message):
    try:
        msg_id = message.chat.id
        bot.send_message(msg_id, result(msg_id), parse_mode="html")
    except Exception as E:
        logger.debug(E)

def timer():
    for i in range(0, 10):
        time.sleep(1)
        yield 9-i
    time.sleep(1)
    yield "READY 🚥 🔴"
    time.sleep(1)
    yield "SET 🚥 🟡"
    time.sleep(1)
    yield "GO 🚥 🟢"

@bot.message_handler(commands=['update'])
def get_update(message):
    msg = f"<b>Update</b>: {_update_.get('update')}\n<b>Description</b>: {_update_.get('description')}"
    bot.send_message(message.chat.id,msg, parse_mode="html")



app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def webhook():
    if request.method == "POST":
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        #update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return 'success', 200
    else:
        abort(400)

@app.route("/")
def index():
    return "Welcome To TargetBoard."

if __name__=="__main__":
    try:
        print("App is running")
        serve(app=app, host='127.0.0.1', port=8443)
    except Exception as E:
        print(E)
