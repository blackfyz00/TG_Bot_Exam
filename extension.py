import pandas as pd
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, sys

def create_object_from_db(to_return, column_name, callback, exam=None, group=None):
    path = os.path.join(os.path.dirname(sys.argv[0]), 'db.xlsx')
    df = pd.read_excel(path)
    list = df[column_name].drop_duplicates().tolist()

    if (to_return == 'keyboard' and column_name=='Время'):
        list = df.query(f"Экзамен == '{exam}' and Группа == '{group}'")
        keyboard = InlineKeyboardMarkup()
        for option in list.itertuples(index=False, name=None):
            keyboard.row(InlineKeyboardButton(str(option[2]), callback_data=callback+'_'+str(option[2])))
        keyboard.row(InlineKeyboardButton('Домой', callback_data='start'))
        return keyboard

    if (to_return == 'keyboard'):
        keyboard = InlineKeyboardMarkup()
        for option in list:
            keyboard.row(InlineKeyboardButton(option, callback_data=callback+'_'+str(option)))
        keyboard.row(InlineKeyboardButton('Домой', callback_data='start'))
        return keyboard
    
    if (to_return == 'list'):
        return list
    
    if (to_return == 'exam_times'):
        filtered_df = df[df['Экзамен'] == exam]
        times_list = filtered_df['Время'].tolist()
        return times_list

    else: 
         return

def create_keyboard_from_list(list, callback):
    keyboard = InlineKeyboardMarkup()
    for option in list:
        keyboard.row(InlineKeyboardButton(option, callback_data=callback+'_'+option))
    keyboard.row(InlineKeyboardButton('Домой', callback_data='start'))
    return keyboard

def get_students(group):
    path = os.path.join(os.path.dirname(sys.argv[0]), 'list_student', f'{group}.txt')
    with open(path, 'r', encoding='utf-8') as file:
        student_list = file.readlines()
    student_list = [line.strip() for line in student_list]
    return student_list

def final_record(user):
    del user[0]
    path = os.path.join(os.path.dirname(sys.argv[0]), 'final_record', f'{user[0]}.xlsx')
    if os.path.exists(path):
        # Читаем существующий файл
        df = pd.read_excel(path)
    else:
        # Создаем новый DataFrame с заданными столбцами
        df = pd.DataFrame([user],columns=['Группа', 'Экзамен', 'Время', 'ФИО'])
        df.to_excel(path, index=False)
        return

    # Объединяем существующий DataFrame с новым
    user = pd.DataFrame([user],columns=['Группа', 'Экзамен', 'Время', 'ФИО'])
    combined_df = pd.concat([df, user],ignore_index=True).drop_duplicates(subset='ФИО', keep='last').reset_index(drop=True)
    # Удаляем дубликаты, оставляя последнее вхождение
    combined_df = combined_df.drop_duplicates(keep='last')
    combined_df.to_excel(path, index=False)

def watch_students(group,exam):
    path = os.path.join(os.path.dirname(sys.argv[0]), 'final_record', f'{group}.xlsx')
    df = pd.read_excel(path)
    df = df.query(f"Экзамен == '{exam}'").sort_values(by='ФИО')
    is_df_empy = df.empty
    df = df.to_string(index=False)
    if is_df_empy == True:
        return 'Пока никто не записался на экзамен :_('
    else:
        return df