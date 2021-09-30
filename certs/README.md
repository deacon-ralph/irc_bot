If you are running your own bot, you will need to generate your own
cert and key using the following command
```bash
openssl req -x509 -newkey rsa:2048 -keyout selfsigned.key -nodes -out selfsigned.cert -sha256 -days 1000
```