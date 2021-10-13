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

    Copyright NOOSCOPE IRC.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.