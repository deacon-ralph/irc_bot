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

## Building + Running container
```bash
# Build container
docker build -t <tag> .

# Run container, assuming you cloned this repo into your home directory ~/
docker run --rm \
-p 6680:6680 \
-v ~/irc_bot/chatter.log:/irc_bot/chatter.log \
-v ~/irc_bot/config.toml:/irc_bot/config.toml \
-v ~/irc_bot/bot_modules:/irc_bot/bot_modules \
-t <tag>
```
