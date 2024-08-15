import logging
import os
from slack_bolt import App
import certifi
import re

from geppetto.utils import is_image_data, lower_string_list
# Set SSL certificate for secure requests
os.environ["SSL_CERT_FILE"] = certifi.where()

# UI roles
USER = "slack_user"
ASSISTANT = "geppetto"


class SlackHandler:

    def __init__(
            self,
            allowed_users,
            bot_default_responses,
            SLACK_BOT_TOKEN,
            SIGNING_SECRET,
            llm_controller):
        """
        Slack Handler receives messages from the slack channel and sends responses back. 
        It also handles commands.
        """
        self.name = 'Geppetto Slack handler'
        self.llm_ctrl = llm_controller
        self.llm = llm_controller.handlers
        self.app = App(signing_secret=SIGNING_SECRET, token=SLACK_BOT_TOKEN)
        self.allowed_users = allowed_users
        self.bot_default_responses = bot_default_responses
        self.thread_messages = {}
        self.commands = {'llms': self.list_llms}

        # Direct Message Event
        @self.app.event("message")
        def handle_direct_messages(body):
            self.handle_event(body)

        # App Mention Event
        @self.app.event("app_mention")
        def handle_app_mentions(body):
            self.handle_event(body)

    def handle_command(self, command, channel_id, thread_id, thread_history):
        """
        Selects the function to handle the specified command.

        For future commands, just add the new command name to the dict 'commands' in SlackHandler
        and implement a new function that does the desired action.
        """
        current_msg = {"role": USER, "content": command}
        thread_history["msgs"].append(current_msg)
        response = self.commands[command](channel_id, thread_id, thread_history)
        thread_history["msgs"].append({"role": ASSISTANT, "content": response})
        self.thread_messages[thread_id] = thread_history

    def handle_message(self, msg, channel_id, thread_id):
        """
        Receives a message from the slack channel and distincs if it is a command or a message. 
        If it is a command, it calls the `handle_command()` function. 
        If it is not, it generates a response using the selected LLM and post it.
        """
        logging.info("Authorized user - Msg received: %s in channel: %s and thread: %s",
                     msg,
                     channel_id,
                     thread_id,
                    )
        msg = msg.strip()  # deleting extra spaces

        # when using the command,
        # msg_copy can be ['llms'] or ['<@...>', 'llms']
        # so we get the last element
        msg_copy = msg.split()
        command = msg_copy[-1]

        if len(msg_copy) <= 2 and command in self.commands:
            thread_history = self.thread_messages.get(thread_id, {"llm": "", "msgs": []})
            self.handle_command(command, channel_id, thread_id, thread_history)
        else:
            # This branch handles general messages
            thread_history = self.thread_messages.get(thread_id, {"llm": "", "msgs": []})
            selected_llm = self.select_llm_from_msg(msg, thread_history["llm"])
            current_usr_msg = {"role": USER, "content": msg}
            
            if thread_history["llm"] == "":
                thread_history["llm"] = selected_llm

            if thread_history["llm"] == selected_llm:
                thread_history["msgs"].append(current_usr_msg)
            else:
                thread_history["llm"] = selected_llm
                thread_history["msgs"] = [thread_history["msgs"][0],
                                          current_usr_msg]
            #send_thought_balloon() tells the user that their message is being processed
            timestamp = self.send_thought_balloon(channel_id, thread_id)
            response_from_llm_api = self.use_prompt_from_thread(selected_llm,
                                                                thread_history,
                                                                channel_id,
                                                                thread_id)
            self.post_response(response_from_llm_api, channel_id, thread_id, thread_history, timestamp)
    
    def use_prompt_from_thread(self, selected_llm, thread_history, channel_id, thread_id):
        """Gets prompt from the thread and generates a response using the selected LLM."""
        prompt = self.llm[selected_llm].get_prompt_from_thread(thread_history["msgs"],
                                                               ASSISTANT,
                                                               USER)
        return self.llm[selected_llm].llm_generate_content(prompt, self.send_message,
                                                           channel_id, thread_id,
                                                           )
            
    def send_thought_balloon(self, channel_id, thread_id):
        """
        Sends a thought balloon to the slack channel to indicate the user 
        that their message is being processed.
        """
        timestamp = None
        response = self.send_message(channel_id,
                                     thread_id,
                                     ":thought_balloon:")
        if response["ok"]:
            timestamp = response["message"]["ts"]
            logging.info("Timestamp of the posted message: %s", timestamp)
        else:
            logging.error("Failed to post the message.")
        return timestamp

    def post_response(self,
                      response_from_llm_api,
                      channel_id,
                      thread_id,
                      thread_history,
                      timestamp,
                      ):
        """Tries to post the response generated by the llm to the slack channel."""
        try:
            if isinstance(response_from_llm_api, str):
                thread_history["msgs"].append({"role": ASSISTANT,
                                               "content": response_from_llm_api})
            self.thread_messages[thread_id] = thread_history

            if is_image_data(response_from_llm_api):
                self.app.client.files_upload_v2(channel=channel_id,
                                                thread_ts=thread_id,
                                                content=response_from_llm_api,
                                                title="Image",
                                                )
                # TODO: images from other apis might not use bytes as
                # datatype
            else:
                logging.info("response from %s: %s" % (self.name, response_from_llm_api))
                # If there are multiple parts, send each part separately
                if isinstance(response_from_llm_api, list):
                    for part in response_from_llm_api:
                        self.app.client.chat_postMessage(channel=channel_id,text=part,
                                                         thread_ts=thread_id, mrkdwn=True)
                else:
                    # If it is a single message, send it normally
                    self.app.client.chat_update(channel=channel_id,
                                                text=response_from_llm_api,
                                                thread_ts=thread_id,
                                                ts=timestamp,
                                                )
        except Exception as e:
            logging.error("Error posting message: %s", e)
            error_msg = "There was an error when posting the message."
            thread_history["msgs"].append({"role": ASSISTANT, "content": error_msg})
            self.thread_messages[thread_id] = thread_history
            self.post_response(error_msg, channel_id,
                               thread_id, timestamp)

    def handle_event(self, body):
        """
        Receives an event from the slack channel and checks if the user that sent the message is allowed to interact with the Geppetto.
        If the user is allowed, it calls the `handle_message()` function.
        """
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
            permission_denied_message = self.bot_default_responses["user"]["permission_denied"]
            self.send_message(channel_id,
                              thread_id,
                              permission_denied_message,
                              "permission_denied")

    def send_message(self, channel_id, thread_id, message, tag="general"):
        """Sends message to the slack channel."""
        logging.info("Sending %s message: %s" % (tag, message))
        return self.app.client.chat_postMessage(channel=channel_id,
                                                text=message,
                                                thread_ts=thread_id,
                                                mrkdwn=True)

    def select_llm_from_msg(self, message, last_llm=''):
        """
        Selects the LLM from the message. If the LLM is not specified, the default LLM is chosen. 
        In this case, ChatGPT.
        """
        mentions = re.findall(r'(?<=\bllm_)\w+', message)
        clean_mentions = [re.sub(r'[\#\!\?\,\;\.]', "", mention)
                          for mention in mentions]
        hashtags = lower_string_list(clean_mentions)
        controlled_llms = self.llm_ctrl.list_llms()
        controlled_llms_l = lower_string_list(controlled_llms)
        check_list = list(set(controlled_llms_l) & set(hashtags))

        if len(check_list) == 1:
            return controlled_llms[controlled_llms_l.index(check_list[0])]
        elif len(check_list) == 0 and last_llm != '':
            return last_llm
        else:
            # default first LLM
            return controlled_llms[0]

    def list_llms(self, channel_id, thread_id, thread_history):
        """
        Implementation of 'llms' command. 
        Lists all available LLMs and sends it to the slack channel.
        """
        availables_assistants = self.llm_ctrl.list_llms()
        format_msg = ["Here are the available AI models!"]

        for assistant in availables_assistants:
            format_msg.append(f"* {assistant} -> llm_{assistant.lower()}")

        reminder = "Example: Using 'llm_gemini' at the start of your message to Geppetto switches to gemini model."
        format_msg.append(reminder)
        formated_msg = '\n'.join(format_msg)
        logging.info("Sending list_llms command %s")
        response = self.send_message(channel_id,
                                     thread_id,
                                     formated_msg)

        if response["ok"]:
            timestamp = response["message"]["ts"]
            self.app.client.chat_update(channel=channel_id,
                                        text=formated_msg,
                                        thread_ts=thread_id,
                                        ts=timestamp,
                                        )
        else:
            logging.error("Failed to post message")
            formated_msg = "There was an error when posting llms list."
        return formated_msg
