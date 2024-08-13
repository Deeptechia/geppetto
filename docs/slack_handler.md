## Slack Handler

## Description

Slack Handler receives messages from the slack channel and sends responses back. It checks if the user is autorized to interact with the bot. It also handles the commands to switch between the available LLMs and to list the available LLMs.

## __init__

SlackHandler(self, allowed_users, bot_default_responses, SLACK_BOT_TOKEN SIGNING_SECRET, llm_controller)

## Class variables

- name = 'Geppetto Slack handler'
- llm_ctrl = llm_controller
- llm = llm_controller.handlers
- app = App(SIGNING_SECRET, SLACK_BOT_TOKEN)
- allowed_users = allowed_users
- bot_default_responses = bot_default_responses
- thread_messages = {}
- commands = ['llms']

#### Notes on the 'commands' variable

For future commands, just add the new command to the list 'commands'. Then modify `handle_command()` to include the new command between the if statements. And finally, create a new function to do the desired action.

## Functions

### **handle_command(command, channel_id, thread_id, thread_history)**

Selects the correct function to handle the specified command.

### **handle_message(self, msg, channel_id, thread_id)**

Receives a message from the slack channel and distincs if it is a command or a message. If it is a command, it calls the `handle_command()` function. If it is not, it uses `select_llm_from_msg()` and generate a response using the selected model.

### **handle_event(self, body)**

Receives an event from the slack channel and checks if the user that sent the message is allowed to interact with the Geppetto. If the user is allowed, it calls the `handle_message()` function.

### **send_message(self, channel_id, thread_id, message, tag="general")**

Sends message to the slack channel.

### **select_llm_from_msg(self, message, last_llm='')**

Selects the LLM from the message. If the LLM is not specified, the default LLM is chosen. In this case, ChatGPT.


### **list_llms(self, channel_id, thread_id, thread_history)**

Uses `send_message()` to send a list of the available LLMs to the slack channel.
