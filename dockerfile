FROM python:3

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install sqlalchemy py-cord python-dotenv

COPY ./bot.py /app

COPY . /app/

CMD ["python", "bot.py"]

# docker run --name technobot --mount type=bind,source="$(pwd)"/data/database.db,target=/app/database.db [IMAGE-NAME]
# docker run --name technobot --mount type=volume,source=bot-data,target=/app test