import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
import extension as exten

bot = telebot.TeleBot(config.token)
users = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
       # Создаем инлайн-клавиатур
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Начать", callback_data='start'))
    bot.send_message(message.chat.id, text=config.init_message, reply_markup=keyboard)

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query_main(call):

    user_id = call.message.chat.id
    if user_id not in users:
        users[user_id] = []

    if call.data == 'start':
        users[user_id] = []
        keyboard_init = InlineKeyboardMarkup()
        keyboard_init.row(InlineKeyboardButton("Записаться на экзамен", callback_data='group_rec'))
        keyboard_init.row(InlineKeyboardButton("Посмотреть списки экзаменуемых и время", 
                                               callback_data='for_teach'))
        bot.send_message(call.message.chat.id, text='Выберите действие', reply_markup=keyboard_init)

    if call.data.startswith('group_rec'):
        substring = call.data[len("group_rec_"):]
        users[user_id].append(substring)
        keyboard_record1 = exten.create_object_from_db(to_return='keyboard', 
                                                       column_name='Группа', callback='exam_rec')
        bot.edit_message_text(chat_id=call.message.chat.id, 
                            message_id=call.message.message_id, 
                            text="Отлично! Выбери группу на запись", reply_markup=keyboard_record1)
        
    if call.data.startswith('for_teach'):
        keyboard_record2 = exten.create_object_from_db(to_return='keyboard', 
                                                       column_name='Группа', 
                                                       callback='teach_watch_subject')
        bot.edit_message_text(chat_id=call.message.chat.id, 
                            message_id=call.message.message_id, 
                            text="Отлично! Выберите группу чтобы просмотреть список", 
                            reply_markup=keyboard_record2)
        
    if call.data.startswith('teach_watch_subject'):
        substring = call.data[len("teach_watch_subject_"):]
        users[user_id].append(substring)
        keyboard_record22 = exten.create_object_from_db(to_return='keyboard', 
                                                        column_name='Экзамен', 
                                                        callback='teach_watch_group')
        bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id, 
                                text=f"Вы выбрали группу {users[user_id][0]}. Выберите экзамен для просмотра", 
                                reply_markup=keyboard_record22)
        
    if call.data.startswith('teach_watch_group'):
        substring = call.data[len("teach_watch_group_"):]
        list_students_exam = exten.watch_students(group=users[user_id][0],exam=substring)
        keyboard_record21 = InlineKeyboardMarkup()
        keyboard_record21.row(InlineKeyboardButton("Домой", callback_data='start'))
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, 
                              text=f'Конечно! Вот список записанных по времени на экзамен:\n\n{list_students_exam}',
                              reply_markup=keyboard_record21)

    if call.data.startswith('exam_rec'):
        substring = call.data[len("exam_rec_"):]
        users[user_id].append(substring)
        keyboard_record3 = exten.create_object_from_db(to_return='keyboard', 
                                                       column_name='Экзамен', 
                                                       callback='exam_time_rec')
        bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id, 
                                text=f"Ты выбрал группу {users[user_id][1]}. Выбери на какой экзамен записаться", 
                                reply_markup=keyboard_record3)

    if call.data.startswith('exam_time_rec'):
        substring = call.data[len("exam_time_rec_"):]
        users[user_id].append(substring)
        keyboard_record4 = exten.create_object_from_db(to_return='keyboard', 
                                                       column_name='Время', 
                                                       exam=users[user_id][2], 
                                                       callback='name_rec', group=users[user_id][1])
        bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id, 
                                text=f"Ты выбрал экзамен {users[user_id][2]}. Выбери время записи", 
                                reply_markup=keyboard_record4)

    if call.data.startswith('name_rec'):
        substring = call.data[len("name_rec_"):]
        users[user_id].append(substring)
        students = exten.get_students(users[user_id][1])
        keyboard_record5 = exten.create_keyboard_from_list(students, callback='prepare_to_record')
        bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id, 
                                text=f"Ты выбрал время {users[user_id][3]}. Выбери себя, чтобы записаться", 
                                reply_markup=keyboard_record5)
        
    if call.data.startswith('prepare_to_record'):
        substring = call.data[len("prepare_to_record_"):]
        users[user_id].append(substring)
        keyboard_record6 = InlineKeyboardMarkup()
        keyboard_record6.row(InlineKeyboardButton("Подтвердить", callback_data='record_to_final_list'))
        keyboard_record6.row(InlineKeyboardButton("Отмена", callback_data='start'))
        bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id, 
                                text=f"Ты выбрал имя {users[user_id][4]}. Подтверди ввод в базу данных", 
                                reply_markup=keyboard_record6)

    if call.data == 'record_to_final_list':
        exten.final_record(users[user_id])
        keyboard_record7 = InlineKeyboardMarkup()
        keyboard_record7.row(InlineKeyboardButton("Домой", callback_data='start'))
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, 
                              text='Вы успешно записались на экзамен',
                              reply_markup=keyboard_record7)

bot.polling()