import json
import logging
import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_sdk import WebClient
import certifi
from srcs.openai_handler import OpenAIHandler

# Set SSL certificate for secure requests
os.environ["SSL_CERT_FILE"] = certifi.where()


# Define global variables
thread_messages = {}


class SlackHandler:
    def __init__(
        self,
        allowed_users,
        SLACK_BOT_TOKEN,
        SLACK_APP_TOKEN,
        SIGNING_SECRET,
        OPENAI_API_KEY,
        DALLE_MODEL,
        CHATGPT_MODEL,
    ):
        self.SLACK_BOT_TOKEN = SLACK_BOT_TOKEN
        self.SLACK_APP_TOKEN = SLACK_APP_TOKEN
        self.SIGNING_SECRET = SIGNING_SECRET
        self.OPENAI_API_KEY = OPENAI_API_KEY
        self.DALLE_MODEL = DALLE_MODEL
        self.CHATGPT_MODEL = CHATGPT_MODEL

        self.openai_scripts = OpenAIHandler(OPENAI_API_KEY, DALLE_MODEL, CHATGPT_MODEL)

        # Initialize Slack client
        self.client = WebClient(token=self.SLACK_BOT_TOKEN)

        self.app = App(signing_secret=SIGNING_SECRET, token=SLACK_BOT_TOKEN)

        def is_allowed(user_id):
            """Check if a user is allowed to interact with the bot."""
            return user_id in allowed_users.values()

        # Define Slack app
        @self.app.event("message")
        def handle_direct_messages(body, say):
            event = body["event"]
            channel_id = event["channel"]
            channel_type = event["channel_type"]
            msg = event["text"]
            thread_id = event.get("thread_ts", None) or event["ts"]
            user_id = event.get("user")
            try:
                event["files"]
                for file_info in files:
                    file_id = file_info["id"]
                    print("file:", file)
            except:
                print("the message does not contain a file")

            print(msg)
            print("user_id", user_id)

            if is_allowed(user_id):
                if "hola" in msg.lower():
                    saludo = "Hola! Mi nombre es Geppetto!"
                    image_path = os.path.join("assets", "GeppettoMini.png")

                    self.client.files_upload(
                        channels=channel_id,
                        initial_comment=saludo,
                        file=image_path,
                        thread_ts=thread_id,
                        filetype="png",
                    )

                    lista_funcionalidades = 'Escribime lo que necesites contestando el hilo iniciado, cada mensaje que envíes generará un hilo de conversación nuevo.\nSi necesitás que genere una imagen, tu mensaje debe incluir la palabra "dalle".'

                    self.app.client.chat_postMessage(
                        channel=channel_id,
                        text=lista_funcionalidades,
                        thread_ts=thread_id,
                    )

                elif "hello" in msg.lower():
                    greet = "Hi! My name is Geppetto!"
                    image_path = os.path.join("assets", "GeppettoMini.png")

                    self.client.files_upload(
                        channels=channel_id,
                        initial_comment=greet,
                        file=image_path,
                        thread_ts=thread_id,
                        filetype="png",
                    )

                    features_list = 'Write to me what you need by replying to the started thread, each message you send will generate a new conversation thread. If you need me to generate an image, your message must include the word "dalle".'

                    self.app.client.chat_postMessage(
                        channel=channel_id, text=features_list, thread_ts=thread_id
                    )

                elif "dalle" in msg:
                    thread_history = thread_messages.get(thread_id, [])
                    thread_history.append({"role": "user", "content": msg})
                    thread_messages[thread_id] = thread_history
                    prompt = "\n".join([m["content"] for m in thread_history])

                    self.client.chat_postMessage(
                        channel=channel_id,
                        username="Dall-E",
                        text="Dall-E está preparando tu imagen",
                        thread_ts=thread_id,
                    )

                    url = self.openai_scripts.text_to_image_url(prompt=prompt)
                    self.openai_scripts.url_to_image(url=url)

                    self.client.files_upload(
                        channels=channel_id,
                        thread_ts=thread_id,
                        username="Dall-E",
                        file=os.path.join("assets", "dall-e.png"),
                        title="respuesta",
                    )

                else:
                    if msg:
                        thread_history = thread_messages.get(thread_id, [])
                        thread_history.append({"role": "user", "content": msg})
                        thread_messages[thread_id] = thread_history
                        prompt = "\n".join([m["content"] for m in thread_history])

                        response = self.app.client.chat_postMessage(
                            channel=channel_id,
                            text=":geppetto: ... :thought_balloon: ...",
                            thread_ts=thread_id,
                        )

                        if response["ok"]:
                            timestamp = response["message"]["ts"]
                            print(f"Timestamp of the posted message: {timestamp}")
                        else:
                            print("Failed to post the message.")

                        response_from_chatgpt = (
                            self.openai_scripts.generate_chatgpt_response(prompt)
                        )
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
                            print(f"Error posting message: {e}")

            else:
                response = self.app.client.chat_postMessage(
                    channel=channel_id,
                    text="El usuario solicitante no pertenece a la lista de usuarios permitidos. Solicite permiso para utilizar la aplicación",
                    thread_ts=thread_id,
                )

        # This gets activated when the bot is tagged in a channel
        @self.app.event("app_mention")
        def handle_app_mentions(body, logger):
            event = body["event"]
            msg = event["text"].split(">")[1]
            channel_id = event["channel"]
            thread_id = event.get("thread_ts", None) or event["ts"]
            user_id = event.get("user")
            username = event.get("username")

            logging.info("%s: %s" % (user_id, msg))

            if is_allowed(user_id):
                if "hola" in msg.lower():
                    saludo = "Hola! Mi nombre es Geppetto!"
                    # Path to the PNG image file you want to attach
                    image_path = os.path.join("assets", "GeppettoMini.png")
                    # Upload the image to Slack
                    self.client.files_upload(
                        channels=channel_id,
                        initial_comment=saludo,
                        file=image_path,
                        thread_ts=thread_id,
                        filetype="png",
                    )

                    lista_funcionalidades = 'Escribime lo que necesites contestando el hilo iniciado, cada mensaje que envies generará un hilo de conversación nuevo.Si necesitás que genere una imagen, tu mensaje debe incluir la palabra "dalle".'

                    # Upload the image to Slack
                    self.app.client.chat_postMessage(
                        channel=channel_id,
                        text=lista_funcionalidades,
                        thread_ts=thread_id,
                    )

                elif "hello" in msg.lower():
                    greet = "Hi! My name is Geppetto!"
                    # Path to the PNG image file you want to attach
                    image_path = os.path.join("assets", "GeppettoMini.png")

                    # Upload the image to Slack
                    self.client.files_upload(
                        channels=channel_id,
                        initial_comment=greet,
                        file=image_path,
                        thread_ts=thread_id,
                        filetype="png",
                    )

                    features_list = 'Write to me what you need by replying to the started thread, each message you send will generate a new conversation thread. If you need me to generate an image, your message must include the word "dalle".'

                    # Upload the image to Slack
                    self.app.client.chat_postMessage(
                        channel=channel_id, text=features_list, thread_ts=thread_id
                    )

                elif "dalle" in msg:
                    thread_history = thread_messages.get(thread_id, [])
                    thread_history.append({"role": "user", "content": msg})
                    thread_messages[thread_id] = thread_history
                    prompt = "\n".join([m["content"] for m in thread_history])

                    self.client.chat_postMessage(
                        channel=channel_id,
                        username="Dall-E",
                        text="Dall-E está preparando tu imagen",
                        thread_ts=thread_id,
                    )

                    url = self.openai_scripts.text_to_image_url(prompt=prompt)
                    self.openai_scripts.url_to_image(url=url)

                    self.client.files_upload(
                        channels=channel_id,
                        thread_ts=thread_id,
                        username="Dall-E",
                        file=os.path.join("assets", "dall-e.png"),
                        title="respuesta",
                    )

                else:
                    thread_history = thread_messages.get(thread_id, [])
                    thread_history.append({"role": "user", "content": msg})
                    thread_messages[thread_id] = thread_history
                    prompt = "\n".join([m["content"] for m in thread_history])

                    response = self.app.client.chat_postMessage(
                        channel=channel_id,
                        text=":geppetto: ... :thought_balloon: ...",
                        thread_ts=thread_id,
                    )

                    if response["ok"]:
                        timestamp = response["message"]["ts"]
                        print(f"Timestamp of the posted message: {timestamp}")
                    else:
                        print("Failed to post the message.")

                    response_from_chatgpt = (
                        self.openai_scripts.generate_chatgpt_response(prompt)
                    )
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
                        print(f"Error posting message: {e}")

            else:
                self.app.client.chat_postMessage(
                    channel=channel_id,
                    text="El usuario solicitante no pertenece a la lista de usuarios permitidos. Solicite permiso para utilizar la aplicación",
                    thread_ts=thread_id,
                )
