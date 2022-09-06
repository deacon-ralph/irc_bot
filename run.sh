FOLDER_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
docker run --rm \
-p 12345-12444:12345-12444 \
-v "$FOLDER_PATH"/ascii_art:/irc_bot/ascii_art \
-v "$FOLDER_PATH"/chatter.log:/irc_bot/chatter.log \
-v "$FOLDER_PATH"/troll.b64:/irc_bot/troll.b64 \
-v "$FOLDER_PATH"/admins.toml:/irc_bot/admins.toml \
-v "$FOLDER_PATH"/config.toml:/irc_bot/config.toml \
-v "$FOLDER_PATH"/bot_modules:/irc_bot/bot_modules \
-t "$1"
