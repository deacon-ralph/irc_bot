FROM python:3.9-bullseye

WORKDIR /irc_bot
COPY . .
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]
