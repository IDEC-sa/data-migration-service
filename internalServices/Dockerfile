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
COPY ./root $APP_HOME/root
COPY ./root $APP_HOME/mediafiles
RUN apt-get update && apt-get install -y wget && apt-get install -y zip
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install --fix-broken -y ./google-chrome-stable_current_amd64.deb

# run python command
# RUN python $APP_HOME/manage.py makemigrations
# RUN python $APP_HOME/manage.py migrate
