# RPC Module

## Installing from PyPi

`pip3 install nooscope_rpc`


Example implementation

```python
import asyncio
import nooscope_rpc.api as api


class Impl(api.IrcImpl):
   async def on_message(self, target, by, message):
      print(target, by, message)
      # do some shit like
      if message == 'hack_a_gibson':
         await self.rpc.send_message(target, 'hacking gibson from RPC')
      elif message.startswith('dieplz'):
         await self.rpc.disconnect()


async def main():
   # endless loop to always try and connect
   while True:
      tcp = api.TcpClient('127.0.0.1', 12345, Impl()) # use bots host ip
      await tcp.connect()
      await tcp.read()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

<br/>
<br/>

#### 🚨Important info before starting to implement your own client not using this library🚨
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


<br/>
<br/>

## Building wheel + src
```bash
# https://packaging.python.org/tutorials/packaging-projects/
python3.9 -m pip install --upgrade build
python3.9 -m build
python3.9 -m twine upload --repository testpypi dist/*
```