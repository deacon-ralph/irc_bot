docker run --rm \
-p 12345-12444:12345-12444 \
-v ~/irc_bot/ascii_art:/irc_bot/ascii_art \
-v ~/irc_bot/chatter.log:/irc_bot/chatter.log \
-v ~/irc_bot/admins.toml:/irc_bot/admins.toml \
-v ~/irc_bot/config.toml:/irc_bot/config.toml \
-v ~/irc_bot/bot_modules:/irc_bot/bot_modules \
-t "$1"
