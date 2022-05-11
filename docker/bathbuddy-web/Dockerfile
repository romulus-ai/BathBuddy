FROM python:3.9

COPY ./app/requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5000/tcp
COPY ./app /app

ENV TZ="Europe/Berlin"

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
