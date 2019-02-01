import json
import os

from django.core.management.base import BaseCommand

from TestTask.settings import BASE_DIR
from chat_app.models import Chat, User, Message
from django.db.models import Q
from multiprocessing import cpu_count, Pool
from django.db import connection, transaction
from django.db.models.signals import m2m_changed


def create_message(message):
    new_message = Message(text=message['text'], date=message.get('date'),
                          user_id=message['user'],
                          chat_id=message['chat'])
    return new_message


def create_user(user):
    new_user = User(username=user['username'], password=user['phash'],
                    city=user['city'],
                    date_joined=user.get('date_joined'),
                    id=user['id'])
    return new_user


def create_chat(chat):
    new_chat = Chat(id=chat['id'], name=chat['name'],
                    created=chat.get('created'))

    for user_id in chat['users']:
        new_chat.users.add(user_id)
        new_chat.save()

    return new_chat


class Command(BaseCommand):
    help = 'This command start writing data to the db'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('SET AUTOCOMMIT=0')
        if options.get('users') or options.get('chats') or options.get('messages'):
            data_type = 'users' if options.get('users') else 'chats' if options.get('chats') else 'messages'

            path = BASE_DIR + '/' + options.get(data_type)

            try:
                with open(path, 'r') as f:
                    data = f.read()
                    data_dict = json.loads(data)[data_type]

            except FileNotFoundError:
                print('File not found')

            else:
                if data_type is 'users':
                    user_pack = []

                    print("Creating users..")

                    for ind, user in enumerate(data_dict):
                        user_pack.append(create_user(user))
                        if ind % 300 == 0 and ind != 0:
                            User.objects.bulk_create(user_pack)
                            user_pack = []

                    User.objects.bulk_create(user_pack)

                elif data_type is 'chats':
                    print("Creating chats..")

                    cursor.execute('SET FOREIGN_KEY_CHECKS=0;')
                    with transaction.atomic():
                        chat_pack = []

                        for ind, chat in enumerate(data_dict):
                            chat_pack.append(create_chat(chat))

                    cursor.execute('SET FOREIGN_KEY_CHECKS=1;')

                else:
                    print("Creating messages..")

                    message_pack = []
                    for ind, message in enumerate(data_dict):

                        message_pack.append(create_message(message))

                        if ind % 300 == 0 and ind != 0:
                            Message.objects.bulk_create(message_pack)
                            message_pack = []

                    Message.objects.bulk_create(message_pack)

        if options['removeall']:
            User.objects.filter(~Q(id=1)).delete()      # Для тестирования
            Chat.objects.all().delete()
            Message.objects.all().delete()

    def add_arguments(self, parser):
        parser.add_argument('-u', '--users', type=str, help='Выгружает json. Принимает путь к файлу.')
        parser.add_argument('-c', '--chats', type=str, help='Выгружает json. Принимает путь к файлу.')
        parser.add_argument('-m', '--messages', type=str, help='Выгружает json. Принимает путь к файлу.')
        parser.add_argument('-r', '--removeall', help='Удаляет все данные')
