docker run --rm \
-p 6680:6680 \
-v ~/irc_bot/ascii_art:/irc_bot/ascii_art \
-v ~/irc_bot/chatter.log:/irc_bot/chatter.log \
-v ~/irc_bot/config.toml:/irc_bot/config.toml \
-v ~/irc_bot/bot_modules:/irc_bot/bot_modules \
-t "$1"
