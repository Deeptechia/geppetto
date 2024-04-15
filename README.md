# Geppetto

![License: AGPLv3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg) 
[![Test Geppetto](https://github.com/Deeptechia/geppetto/actions/workflows/tests-python.yml/badge.svg?branch=main)](https://github.com/Deeptechia/geppetto/actions/workflows/tests-python.yml)

<p align="center">
  <img src="./assets/GeppettoMini.png" alt="Geppetto Logo"/>
</p>

Geppetto is a sophisticated Slack bot that facilitates seamless interaction with multiple AI models, including OpenAI's ChatGPT-4, DALL-E-3, and Google's Gemini model. This versatility allows for a variety of AI-driven interactions tailored to team requirements. This project is brought to you by [DeepTechia](https://deeptechia.io/), where the future of technology meets today’s business needs.

## Features

1. **Flexible AI Model Integration and System Management:**
   - Users can seamlessly switch between ChatGPT-4-turbo and Gemini to suit their specific interaction needs. ChatGPT-4-turbo is set as the default model.
   - You can send direct messages to the application and receive responses from Geppetto. Each message generates a conversation thread, and the application uses the message history to formulate coherent responses.
   - The newly introduced LLM controller component allows the user to manage multiple AI models.
   - Simplified installation and management process, facilitated by Docker deployment.

2. **Advanced Image Generation with DALL-E-3:**
   - Leverage DALL-E-3 to generate creative and contextually relevant images directly within Slack conversations.


![Geppetto](/assets/Geppetto.gif)

## Usage Rules

- **Direct Messages:**
   - It is not necessary to mention the application with "@" in direct messages.
   - Each direct message generates a conversation thread.

- **Slack Channels:**
   - You must mention the application with "@" to interact in channels.

- **Allowed Users:**
   - Only authorized users can interact with the application. Set allowed users in [./config/allowed-slack-ids.json](https://github.com/CoinFabrik/geppetto/blob/main/config/allowed-slack-ids.json).

## Configuration

### Slack Configuration

Follow these steps to configure Slack for your application:

#### Create App
1. **Modify `manifest-dev.yaml`**: Update fields under `display_information` and `bot_user` to customize Geppetto for your personal use.
2. **Create New App**:
    - Go to the [Slack API](https://api.slack.com) and navigate to *Your Apps*.
    - Click on *Create New App*.
    - Choose *Create from manifest*, select *yaml* and paste the contents of the modified `manifest-dev.yaml` file.
    - Click *Next* and then *Create* the application.

#### Save App Credentials

At the **Basic Information** section:
  1. Under the *App Credentials* subsection, save the following:
     - **Signing Secret**.
  2. In the *App-Level Tokens* subsection:
     - Click on *Generate Tokens and Scopes*.
     - Set a Token Name and assign the scope to `connections:write`.
     - Generate and save the **App-Level Token** for later use (this will be your `SLACK_APP_TOKEN`).

At the **Install App** section:
  3. Under the Install App to Your Team subsection:
     - Save the **Bot User OAuth Token** (this will be your `SLACK_BOT_TOKEN`).
     - Install or Request the installation of your app to your Workspace (if it requires approval from an owner of your Slack workspace).


### Environment Configuration

Before running the application, copy the `.configuration/.env.example` file into a new `.configuration/.env` file. Modify the following environment variables in this file:

- `SLACK_BOT_TOKEN`: Your Slack bot token (This is the Bot User OAuth Token, it should start with 'xoxb').
- `SLACK_APP_TOKEN`: Your Slack application token (This is the App-Level Token, it should start with 'xapp').
- `OPENAI_API_KEY`: Your OpenAI API key.
- `SIGNING_SECRET`: Your Signing secret to verify Slack requests (from your Slack App Credentials).
- `DALLE_MODEL`: The OpenAI DALL-E-3 model.
- `CHATGPT_MODEL`: The OpenAI ChatGPT-4 model.

## Deployment

Before you begin, ensure you have the following installed:
- Python (version 3.x recommended)
- pip (Python package manager)
- poetry

Follow these steps to deploy Geppetto:

1. Download the repository and open your terminal.
2. Navigate to the repository directory and install dependencies with `poetry install`.
3. Run the application by entering `poetry run geppetto` in the terminal.

Enjoy interacting with ChatGPT-4 and DALL-E-3 on Slack!

## Docker
To run geppetto in a docker container, when you have Docker & Docker compose installed:
1. Move docker-compose.example.yml to docker-compose.yml with customizing where your config folder resides
2. Change the config values in config/.env
3. Run docker compose build
4. Run docker compose up -d

## Tests

In order to run the tests, execute the following command from the root folder:
`python -m unittest`

or `python -m unittest -v` for a verbose more specific output

## About DeepTechia

We are DeepTechia, where the future of technology meets today’s business needs. As pioneers in the digital realm, we’ve made it our mission to bridge the gap between innovation and practicality, ensuring that businesses not only survive but thrive in an ever-evolving technological landscape.

Born from a passion for cutting-edge technology and a vision for a digitally integrated future, DeepTechia was established to be more than just a tech consultancy. We are visionaries, strategists, and implementers, dedicated to pushing the boundaries of what’s possible while ensuring real-world applicability.

Over the years, we’ve had the privilege of partnering with over 500 companies from a wide range of industries, guiding them through the intricate maze of digital transformation.

At DeepTechia, we believe in a future where technology enhances every facet of business operations, from efficiency and growth to innovation and customer engagement. Our commitment is unwavering: to provide solutions that are forward-thinking yet grounded, innovative yet practical.

We’re not just your tech consultants; we’re your partners in crafting a digital future that’s bright, secure, and boundless.

## License

Geppetto is licensed and distributed under the AGPLv3 license. [Contact us](https://deeptechia.io/contact/) if you're looking for an exception to the terms.
