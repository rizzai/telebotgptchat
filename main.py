# please, read documentaion first/пожалуйста, сначала прочтите документацию
import telebot
import os
import requests
import speech_recognition as sr
import librosa
import torch
import soundfile as sf
import openai
import soundfile as sf
from omegaconf import OmegaConf
import sounddevice as sd
from telebot import types

gender = None
text = None
voiceortext = None
promptfemale = "Use your own GPT prompt for female here"
promptmale = "Use your own GPT prompt for male here"

flag = False
recognizer = sr.Recognizer()
openai.api_key = "YOUR OPENAI TOKEN"
TOKEN = "YOUR TELEBOT TOKEN"
bot = telebot.TeleBot(token=TOKEN)
messages = []
prompt = None


@bot.message_handler(commands=['start'])
def start_message(message):
    messages = []
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(
        'Ответ голосом.', callback_data='button1')
    button2 = types.InlineKeyboardButton(
        'Ответ текстом.', callback_data='button2')
    markup.add(button1, button2)
    bot.send_message(
        message.chat.id, "Здравствуйте! Это - программа-болталка. Выберите режим: ", reply_markup=markup)
    print(message.from_user.first_name)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global voiceortext
    global gender
    global messages
    if call.data == 'button1':
        voiceortext = 0
        markup = types.InlineKeyboardMarkup()
        button3 = types.InlineKeyboardButton(
            'Девушка', callback_data='button3')
        button4 = types.InlineKeyboardButton(
            'Мужчина', callback_data='button4')
        markup.add(button3, button4)
        bot.send_message(
            call.message.chat.id, 'Отлично. Вы выбрали режим ответа голосом. Выберите пол собеседника:', reply_markup=markup)
    elif call.data == 'button2':
        voiceortext = 1
        markup = types.InlineKeyboardMarkup()
        button3 = types.InlineKeyboardButton(
            'Девушка', callback_data='button3')
        button4 = types.InlineKeyboardButton(
            'Мужчина', callback_data='button4')
        markup.add(button3, button4)
        bot.send_message(
            call.message.chat.id, 'Отлично. Вы выбрали режим ответа текстом. Выберите пол собеседника:', reply_markup=markup)
    elif call.data == 'button3':
        gender = "female"
        messages.append({"role": "user", "content": promptfemale})
        bot.send_message(call.message.chat.id,
                         'Хорошо. Чат начат!')
    elif call.data == 'button4':
        gender = "male"
        messages.append({"role": "user", "content": promptmale})
        bot.send_message(call.message.chat.id,
                         'Хорошо. Чат начат!')



def ask(textuser):
    global messages
    print(textuser)
    print(messages)
    messages.append({"role": "user", "content": textuser})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    chat_response = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": chat_response})
    print(chat_response)
    return chat_response


def syntesis(text, gender):
    language = 'ru'
    model_id = 'v3_1_ru'
    device = torch.device('cpu')
    model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                         model='silero_tts',
                                         language=language,
                                         speaker=model_id)
    model.to(device)
    sample_rate = 48000
    if gender == "male":
        speaker = "aidar"
    else:
        speaker = "baya"
    put_accent = True
    put_yo = True
    audio = model.apply_tts(text=text,
                            speaker=speaker,
                            sample_rate=sample_rate,
                            put_accent=put_accent,
                            put_yo=put_yo)
    sf.write('audio.mp3', audio, int(48000))


def convert(path):
    global text
    with sr.AudioFile(path) as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language='ru-RU')  # you can use any language instead of russian ofc


@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    global voiceortext
    global gender
    print(message.from_user.first_name)
    try:
        if gender == "female":
            if voiceortext == 0:
                textanswer = ask(message.text)
                syntesis(textanswer, gender)
                audio = open("audio.mp3", "rb")
                bot.send_voice(message.chat.id, audio)
                audio.close()
            elif voiceortext == 1:
                textanswer = ask(message.text)
                bot.reply_to(message, textanswer)

        elif gender == "male":
            if voiceortext == 0:
                textanswer = ask(message.text)
                syntesis(textanswer, gender)
                audio = open("audio.mp3", "rb")
                bot.send_voice(message.chat.id, audio)
                audio.close()
            elif voiceortext == 1:
                textanswer = ask(message.text)
                bot.reply_to(message, textanswer)
        else:
            bot.reply_to(message, "Задайте параметры голоса/типа ответа через /start!")
    except:
        bot.reply_to(message, "Ошибка с генерацией!")

        
@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    try:
        print(message.from_user.first_name)
        voice = message.voice
        file_id = voice.file_id
        file_info = bot.get_file(file_id)
        file = requests.get(
            'https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
        with open('voice_message.mp3', 'wb') as f:
            f.write(file.content)
        y, sr = librosa.load('voice_message.mp3', sr=16000)
        file1 = 'voice_message.wav'
        sf.write(file1, y, sr)
        bot.reply_to(message, "Процесс может занять некоторое время...")
        try:
            convert("voice_message.wav")
            if gender == "female":
                if voiceortext == 0:
                    prompt = promptfemale + text
                    textanswer = ask(prompt)
                    syntesis(textanswer, gender)
                    audio = open("audio.mp3", "rb")
                    bot.send_voice(message.chat.id, audio)
                    audio.close()
                elif voiceortext == 1:
                    prompt = promptfemale + text
                    textanswer = ask(prompt)
                    bot.reply_to(message, textanswer)

            elif gender == "male":
                if voiceortext == 0:
                    prompt = promptmale + text
                    textanswer = ask(prompt)
                    syntesis(textanswer, gender)
                    audio = open("audio.mp3", "rb")
                    bot.send_voice(message.chat.id, audio)
                    audio.close()
                elif voiceortext == 1:
                    prompt = promptmale + text
                    textanswer = ask(prompt)
                    bot.reply_to(message, textanswer)
                os.remove("voice_message.wav")
                os.remove("voice_message.mp3")
                bot.reply_to(message, textanswer)
        except:
            bot.send_message(
                "Ошибка распознования голоса: попробуйте говорить чётче.")
    except:
        bot.reply_to(message, "Ошибка с генерацией!")


@bot.message_handler(commands=['clear'])
def clear(message):
    global messages
    if len(messages) > 1:
        for i in reversed(range(1,len(messages))):
            messages.pop(i)
        bot.reply_to(message, "История сообщений удалена!")
    else:
        bot.send_message(message.chat.id, "История и так пуста.")


bot.polling()
