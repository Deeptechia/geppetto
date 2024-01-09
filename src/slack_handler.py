import logging
import os
from slack_bolt import App
from slack_sdk import WebClient
import certifi
from srcs.openai_handler import OpenAIHandler

# Set SSL certificate for secure requests
os.environ["SSL_CERT_FILE"] = certifi.where()

# Define global variables
thread_messages = {}


# TODO: maybe use a separate config file with all the dictionaries/descriptions


class SlackHandler:
    def __init__(
        self,
        allowed_users,
        SLACK_BOT_TOKEN,
        SIGNING_SECRET,
        OPENAI_API_KEY,
        DALLE_MODEL,
        CHATGPT_MODEL,
    ):
        self.openai_scripts = OpenAIHandler(OPENAI_API_KEY, DALLE_MODEL, CHATGPT_MODEL)

        # Initialize Slack client
        self.client = WebClient(token=SLACK_BOT_TOKEN)

        # Define Slack app
        self.app = App(signing_secret=SIGNING_SECRET, token=SLACK_BOT_TOKEN)

        # Initialize instances for handling messages and mentions
        self.slack_methods = SlackMethods(
            self.app, self.client, allowed_users, self.openai_scripts
        )

        # Direct Message Event
        @self.app.event("message")
        def handle_direct_messages(body):
            self.slack_methods.handle_event(body)

        # App Mention Event
        @self.app.event("app_mention")
        def handle_app_mentions(body):
            self.slack_methods.handle_event(body)


class SlackMethods:
    def __init__(
        self, app: App, client: WebClient, allowed_users, openai_scripts: OpenAIHandler
    ):
        self.app = app
        self.client = client
        self.allowed_users = allowed_users
        self.openai_scripts = openai_scripts

    def handle_event(self, body):
        event = body["event"]
        msg = event["text"]
        channel_id = event["channel"]
        thread_id = event.get("thread_ts", None) or event["ts"]
        user_id = event.get("user")

        # TODO: add logging information about the current event
        logging.info("%s: %s" % (user_id, msg))

        # Check if user is allowed
        if self.is_allowed(user_id):
            if "hola" in msg.lower():
                self.handle_greeting_spanish(channel_id, thread_id)
            elif "hello" in msg.lower():
                self.handle_greeting_english(channel_id, thread_id)
            elif "dalle" in msg.lower():
                self.handle_dalle(msg, channel_id, thread_id)
            elif msg:
                self.handle_default(msg, channel_id, thread_id)
        else:
            self.send_permission_denied(channel_id, thread_id)

    def is_allowed(self, user_id):
        """Check if a user is allowed to interact with the bot."""
        return user_id in self.allowed_users.values()

    def handle_greeting_spanish(self, channel_id, thread_id):
        SALUDO = "Hola! Mi nombre es Geppetto!"
        image_path = os.path.join("assets", "GeppettoMini.png")  

        self.client.files_upload(
            channels=channel_id,
            initial_comment=SALUDO,
            file=image_path,
            thread_ts=thread_id,
            filetype="png",
        )

        LISTA_FUNCIONALIDADES = (
            "Escribime lo que necesites contestando el "
            "hilo iniciado, cada mensaje que envíes generará un hilo de conversación "
            "nuevo.\nSi necesitás que genere una imagen, "
            'tu mensaje debe incluir la palabra "dalle".'
        )

        self.app.client.chat_postMessage(
            channel=channel_id,
            text=LISTA_FUNCIONALIDADES,
            thread_ts=thread_id,
        )

    def handle_greeting_english(self, channel_id, thread_id):
        GREET = "Hi! My name is Geppetto!"
        image_path = os.path.join("assets", "GeppettoMini.png")  

        self.client.files_upload(
            channels=channel_id,
            initial_comment=GREET,
            file=image_path,
            thread_ts=thread_id,
            filetype="png",
        )

        FEATURES_LIST = (
            "Write to me what you need by replying to the started"
            "thread, each message you send will generate a new conversation thread.\n"
            "If you need me to generate an image, your message must include the"
            'word "dalle".'
        )

        self.app.client.chat_postMessage(
            channel=channel_id, text=FEATURES_LIST, thread_ts=thread_id
        )

    def handle_dalle(self, msg, channel_id, thread_id):
        _, prompt = self.thread_prompt(msg, thread_id)

        logging.info("prompt: %s" % (prompt))

        self.client.chat_postMessage(
            channel=channel_id,
            username="Dall-E",
            text="Dall-E está preparando tu imagen",
            thread_ts=thread_id,
        )

        url = self.openai_scripts.text_to_image_url(prompt=prompt)
        self.openai_scripts.url_to_image(url=url)
        # TODO: if image is returned, we could use it in the response
        self.client.files_upload(
            channels=channel_id,
            thread_ts=thread_id,
            username="Dall-E",
            file= os.path.join("assets", "dall-e.png"), 
            title="respuesta",
        )

    def handle_default(self, msg, channel_id, thread_id):
        thread_history, prompt = self.thread_prompt(msg, thread_id)

        response = self.app.client.chat_postMessage(
            channel=channel_id,
            text=":geppetto: ... :thought_balloon: ...",
            thread_ts=thread_id,
        )

        if response["ok"]:
            timestamp = response["message"]["ts"]
            # TODO: use logger here
            print(f"Timestamp of the posted message: {timestamp}")
        else:
            print("Failed to post the message.")

        response_from_chatgpt = self.openai_scripts.generate_chatgpt_response(prompt)
        thread_history.append({"content": response_from_chatgpt})
        thread_messages[thread_id] = thread_history

        try:
            self.app.client.chat_update(
                channel=channel_id,
                text=response_from_chatgpt,
                thread_ts=thread_id,
                ts=timestamp,
            )
        except Exception as e:
            # TODO: use logger here
            print(f"Error posting message: {e}")

    def send_permission_denied(self, channel_id, thread_id):
        self.app.client.chat_postMessage(
            channel=channel_id,
            text="El usuario solicitante no pertenece a la lista de\
                 usuarios permitidos. Solicite permiso para utilizar la aplicación",
            thread_ts=thread_id,
        )

    def thread_prompt(self, msg, thread_id):
        thread_history = thread_messages.get(thread_id, [])
        thread_history.append({"role": "user", "content": msg})
        thread_messages[thread_id] = thread_history
        prompt = "\n".join([m["content"] for m in thread_history])
        return thread_history, prompt
