from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import os
import asyncio
from dotenv import load_dotenv
from constants import TWITCH_CHANNEL, TWITCH_MAX_MESSAGE_LENGTH
from modules.module import Module


class TwitchClient(Module):
    def __init__(self, signals, enabled=True):
        super().__init__(signals, enabled)
        self.chat = None
        self.twitch = None
        # Instantiate the API class and assign to self.API
        self.API = TwitchAPI(self)

    async def run(self):
        load_dotenv()
        APP_ID = os.getenv("TWITCH_APP_ID")
        APP_SECRET = os.getenv("TWITCH_SECRET")
    # print(f"[DEBUG] Loaded Twitch credentials: APP_ID={APP_ID}, APP_SECRET={'SET' if APP_SECRET else 'NOT SET'}, CHANNEL={TWITCH_CHANNEL}")
        USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

        # Define event handlers inside the run method
        async def on_ready(ready_event: EventData):
            await ready_event.chat.join_room(TWITCH_CHANNEL)
            print(f'[TWITCH] Joined channel: {TWITCH_CHANNEL}')

        async def on_message(msg: ChatMessage):
            if not self.enabled:
                return
            if len(msg.text) > TWITCH_MAX_MESSAGE_LENGTH:
                return
            print(f'[TWITCH] {msg.user.name}: {msg.text}')
            if len(self.signals.recentTwitchMessages) > 10:
                self.signals.recentTwitchMessages.pop(0)
            self.signals.recentTwitchMessages.append(f"{msg.user.name} : {msg.text}")
            self.signals.recentTwitchMessages = self.signals.recentTwitchMessages

        async def on_sub(sub: ChatSub):
            print(f'New subscription in {sub.room.name}:\n'
                  f'  Type: {sub.sub_plan}\n'
                  f'  Message: {sub.sub_message}')

        async def test_command(cmd: ChatCommand):
            if len(cmd.parameter) == 0:
                await cmd.reply('you did not tell me what to reply with')
            else:
                await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')

        if not self.enabled:
            return

    # print("[DEBUG] Attempting to connect to Twitch API...")
        twitch = await Twitch(APP_ID, APP_SECRET)
    # print("[DEBUG] Twitch API instance created.")
        auth = UserAuthenticator(twitch, USER_SCOPE)
        token, refresh_token = await auth.authenticate()
    # print("[DEBUG] Twitch authentication complete.")
        await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)
    # print("[DEBUG] User authentication set.")

        chat = await Chat(twitch)
    # print("[DEBUG] Chat instance created.")

        self.twitch = twitch
        self.chat = chat

        chat.register_event(ChatEvent.READY, on_ready)
        chat.register_event(ChatEvent.MESSAGE, on_message)
        chat.register_event(ChatEvent.SUB, on_sub)
        chat.register_command('reply', test_command)

        chat.start()

        try:
            while True:
                if self.signals.terminate:
                    self.chat.stop()
                    await self.twitch.close()
                    return
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Exception in TwitchClient.run: {e}")


# API class for TwitchClient
class TwitchAPI:
    def __init__(self, outer):
        self.outer = outer

    def set_twitch_status(self, status):
        self.outer.enabled = status
        # If chat was disabled, clear recentTwitchMessages
        if not status:
            self.outer.signals.recentTwitchMessages = []
        self.outer.signals.sio_queue.put(('twitch_status', status))

    def get_twitch_status(self):
        return self.outer.enabled
