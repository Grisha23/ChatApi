service mysql start

mysql --user="root" --password="222" --execute='CREATE DATABASE Chats DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;'
mysql --user="root" --password="222" --execute="CREATE USER 'django_chats' IDENTIFIED BY '222';"
mysql --user="root" --password="222" --execute="GRANT ALL PRIVILEGES ON Chats.* TO 'django_chats';"
mysql --user="root" --password="222" --execute="FLUSH PRIVILEGES;"

python manage.py migrate

echo "Fill base start"

python manage.py data_parser -u 'users.json'
python manage.py data_parser -c 'chats.json'
python manage.py data_parser -m 'messages.json'

echo "Fill base end"
echo "Ready"

gunicorn TestTask.wsgi --bind 0.0.0.0:80 --workers=8