FROM python:3.9-bullseye

WORKDIR /irc_bot
COPY . .
RUN sed -i 's/MinProtocol = TLSv1.2/MinProtocol = TLSv1.0/' /etc/ssl/openssl.cnf
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]
