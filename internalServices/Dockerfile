FROM python:3.10


# set environment variables
ENV APP_HOME=/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR $APP_HOME

# update pip, install dependencies
RUN pip install --upgrade pip 
COPY ./requirements.txt $APP_HOME
RUN pip install -r requirements.txt

# copy app folder
COPY . $APP_HOME

# run python command
# RUN rm -r ./*/migrations/*
RUN python manage.py makemigrations
# RUN python manage.py migrate
# RUN python manage.py collectstatic --noinput --clear


