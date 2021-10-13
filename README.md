# IRC BOT

## Getting Started
1. Copy `example_conf.toml` to `config.toml` and update settings appropriately
```bash
cp example_conf.toml config.toml
```
2. Create the following files
```bash
echo -en "Hello world.\nThis is the file used for markov." >> chatter.log 
```

3. Generate cacert + key
```bash
cd certs
openssl req -x509 -newkey rsa:2048 -keyout selfsigned.key -nodes -out selfsigned.cert -sha256 -days 1000
```

## Building + Running container
```bash
# Build container
docker build -t <tag> .

# Run container, assuming you cloned this repo into your home directory ~/
docker run --rm \
-p 6680:6680 \
-v ~/irc_bot/ascii_art:/irc_bot/ascii_art \
-v ~/irc_bot/chatter.log:/irc_bot/chatter.log \
-v ~/irc_bot/config.toml:/irc_bot/config.toml \
-v ~/irc_bot/bot_modules:/irc_bot/bot_modules \
-t <tag>
```

### GLHF, CHAT HARD

![alt GNAA Public Health Message](irc-covid-message.png)


License
=======
![name](WTFPL.jpg)

    DO WHAT THE FUCK EVER YOU WANT TO PUBLIC LICENSE
            Version 1.0, September 2021

    Copyright (C) 2021 NOOSCOPE IRC

    Everyone is permitted to copy and distribute verbatim or modified
    copies of this license document. Nobody is liable for anything,
    no promises are made about this software, and it is without warranty.
    You may use this software in any way for any reason except satanism or 
    abortions or divorces.
 
           DO WHAT THE FUCK EVER YOU WANT TO PUBLIC LICENSE
    TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

    0. You just DO WHAT THE FUCK YOU WANT TO, INSHALLAH!