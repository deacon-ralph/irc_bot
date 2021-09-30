# RPC Module

## Building
```bash
# https://packaging.python.org/tutorials/packaging-projects/
python3.9 -m pip install --upgrade build
python3.9 -m build
python3.9 -m twine upload --repository testpypi dist/*
```

## Installing from PyPi

`pip3 install nooscope_rpc`

### 🚨Important info before starting to implement your own client🚨
*Messages are terminated by a nullbyte 0x00. 
This means at the end of any message you send, add 0x00 byte. Any message you 
receive from the server will be ended with 0x00*

## Info for those who want to implement their own client

### Supported Messages you can send from the client
1. Sending a message to a channel or user
   - `CLIENT_CMD:SEND_MESSAGE:{"target": "#channel/user", "message": "hello world:"}`
2. Telling the server you are disconnecting
   - `CLIENT_END:`

### Supported Message you can receive from the server
1. On message in a channel or from user
   - `SERVER_EVENT:ON_MESSAGE:{"target": "#channel/user", "by": "user_who_sent_msg", "message": "hello world"}`
2. On RPC Server restarting
   - `SERVER_EVENT:RESTARTING`


## Example implementation using the python lib

```python
import asyncio
import nooscope_rpc.api as api


class Impl(api.IrcImpl):
   async def on_message(self, target, by, message):
      print(target, by, message)
      # do some shit like
      if message == 'hack_a_gibson' and by == 'ZeroCool':
         await self.rpc.send_message('#test', 'hacking gibson from RPC')
      elif message.startswith('dieplz'):
         await self.rpc.disconnect()


async def main():
   # endless loop to always try and connect
   while True:
      loop = asyncio.get_event_loop()
      tcp = api.TcpClient('127.0.0.1', 12345, Impl(), loop)
      await tcp.connect()
      await tcp.read()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```