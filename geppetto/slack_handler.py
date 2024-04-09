import logging
import os
from slack_bolt import App
import certifi

from geppetto.utils import is_image_data

# Set SSL certificate for secure requests
os.environ["SSL_CERT_FILE"] = certifi.where()

# wip: TBD switcher
DEFAULT_LLM = "OpenAI"
# DEFAULT_LLM = "Gemini"

# UI roles
USER = "slack_user"
ASSISTANT = "geppetto"

class SlackHandler:
    thread_messages = {}

    def __init__(
        self,
        allowed_users,
        bot_default_responses,
        SLACK_BOT_TOKEN,
        SIGNING_SECRET,
        GEMINI_MODEL,
        llm_controller
    ):
        self.name = 'Geppetto Slack handler'
        self.llm_ctrl = llm_controller.handlers
        self.app = App(signing_secret=SIGNING_SECRET, token=SLACK_BOT_TOKEN)
        self.allowed_users = allowed_users
        self.bot_default_responses = bot_default_responses

        # Direct Message Event
        @self.app.event("message")
        def handle_direct_messages(body):
            self.handle_event(body)

        # App Mention Event
        @self.app.event("app_mention")
        def handle_app_mentions(body):
            self.handle_event(body)

    def handle_message(self, msg, channel_id, thread_id):
        logging.info(
            "Authorized user - Msg received: %s in channel: %s and thread: %s",
            msg,
            channel_id,
            thread_id,
        )
        thread_history = self.thread_messages.get(thread_id, [])
        thread_history.append({"role": USER, "content": msg})

        response = self.send_message(
            channel_id,
            thread_id,
            ":geppetto: :thought_balloon: ..."
        )

        if response["ok"]:
            timestamp = response["message"]["ts"]
            logging.info("Timestamp of the posted message: %s", timestamp)
        else:
            logging.error("Failed to post the message.")

        prompt = self.llm_ctrl[DEFAULT_LLM].get_prompt_from_thread(thread_history, ASSISTANT, USER)
        response_from_llm_api = self.llm_ctrl[DEFAULT_LLM].llm_generate_content(
            prompt,
            self.send_message,
            channel_id,
            thread_id,
        )
        if isinstance(response_from_llm_api, str):
            thread_history.append({"role": ASSISTANT, "content": response_from_llm_api})

        self.thread_messages[thread_id] = thread_history

        try:
            if is_image_data(response_from_llm_api):
                self.app.client.files_upload_v2(
                    channel=channel_id,
                    thread_ts=thread_id,
                    content=response_from_llm_api,
                    title="Image",
                )  # TODO: images from other apis might not use bytes as datatype
            else:
                logging.info(
                    "response from %s: %s" % (self.name, response_from_llm_api)
                )
                self.app.client.chat_update(
                    channel=channel_id,
                    text=response_from_llm_api,
                    thread_ts=thread_id,
                    ts=timestamp,
                )
        except Exception as e:
            logging.error("Error posting message: %s", e)

    def handle_event(self, body):
        event = body["event"]
        msg = event["text"]
        channel_id = event["channel"]
        thread_id = event.get("thread_ts", None) or event["ts"]
        user_id = event.get("user")

        logging.info("Received event: %s" % event)
        logging.info("%s: %s" % (user_id, msg))

        # Check if user is allowed or * as wildcard to all users
        if "*" in self.allowed_users.values() or user_id in self.allowed_users.values():
            self.handle_message(msg, channel_id, thread_id)
        else:
            permission_denied_message = self.bot_default_responses["user"][
                "permission_denied"
            ]
            self.send_message(channel_id,
                              thread_id,
                              permission_denied_message,
                              "permission_denied")

    def send_message(self, channel_id, thread_id, message, tag="general"):
        logging.info(
            "Sending %s message: %s"
            % (tag, message)
        )
        return self.app.client.chat_postMessage(
            channel=channel_id,
            text=message,
            thread_ts=thread_id,
            mrkdwn=True
        )
