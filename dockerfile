FROM python:3.6

WORKDIR /app

COPY . /app/.

RUN apt-get update \
    && apt-get install -y mysql-server --no-install-recommends \
    && apt-get clean \
    && pip install PyMySQL \
    && pip install mysqlclient \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV DJANGO_SETTINGS_MODULE TestTask.settings

RUN pip install --upgrade setuptools

RUN pip install --upgrade -r requirements.txt

EXPOSE 80

CMD ["bash", "run.sh"]