"""constants used by api"""

SEPARATOR_B = b'\x00'  # separator used to separate socket msgs (bytes)
SEPARATOR_S = '\x00'  # separator used to separate socket msgs (string)

CLIENT_CMD = 'CLIENT_CMD:'  # command issued by client to server
CLIENT_END = 'CLIENT_END:'  # sent by the client, means to END connection
SERVER_END = 'SERVER_END:'  # sent by the server when termination connection
SERVER_EVENT = 'SERVER_EVENT:'  # sent by server when irc event occurs
SERVER_CMD = 'SERVER_CMD:'  # command issued by server to client

ON_MESSAGE = f'{SERVER_EVENT}ON_MESSAGE:'  # send by server on message
SEND_MESSAGE = f'{CLIENT_CMD}SEND_MESSAGE:'
RESTARTING = f'{SERVER_EVENT}RESTARTING'  # sent when server is restarting
