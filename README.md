
<p align="center">
  <img src="./assets/GeppettoMini.png" alt="Geppetto Logo"/>
</p>

# 🤖 Geppetto

![License: AGPLv3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg) 
![Geppetto Tests](https://github.com/Deeptechia/geppetto/actions/workflows/tests-python.yml/badge.svg)

Geppetto is a sophisticated Slack bot 🤖 that facilitates seamless interaction with multiple AI models, including OpenAI's ChatGPT-4, DALL-E-3, and Google's Gemini model. This versatility allows for a variety of AI-driven interactions tailored to team requirements. This project is brought to you by [DeepTechia](https://deeptechia.io/), where the future of technology meets today’s business needs. 🚀

## ⭐️ Key Features

### 🔄 Flexible AI Model Integration and System Management

- Toggle effortlessly between AI models like ChatGPT and Gemini to suit your specific requirements. ChatGPT model gpt4-turbo is set as the default model
- Initiate dynamic conversation threads by directly messaging Geppetto.
- Manage multiple AI models with the advanced LLM controller component.
- Enjoy an easy setup and management experience, powered by Docker 🐳.

### 🎨 Advanced Image Generation

- Utilize DALL-E-3 to create innovative and contextually apt images during your Slack conversations.

![Geppetto](/assets/Geppetto.gif)

## 👨‍💻 Usage Guidelines

### 📩 Direct Messages

- Directly messaging the bot does not require mentioning it with "@".
- Each direct message generates a conversation thread.

### 💬 Slack Channels

- Invoke Geppetto in channel discussions by mentioning it with "@".

### 🔒 Allowed Users 🔒

- Access is granted only to users listed in the [allowed users configuration file](./config/allowed-slack-ids.json).

## 🔀 Switching AI Models

- To switch between ChatGPT and Gemini, or other models, include the following commands in your message:
  - `llm_openai` to use ChatGPT
  - `llm_gemini` to use Gemini

## 🛠️ Setup and Configuration

### 🔧 Slack App Configuration

1. **Modify App**:
   - **Edit `manifest-dev.yaml`**: Adjust fields under `display_information` and `bot_user` to tailor Geppetto for your needs.
2. **Create App**:
   - Go to the  [Slack API](https://api.slack.com) and navigate to *Your Apps*.
   - Click on *Create New App*.
   - Choose *Create from manifest*, select *yaml* and paste the contents of the modified `manifest-dev.yaml` file.
   - Click *Next* and then *Create* the application.

3. **Save App Credentials** 🗝️

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

4. **Environment Setup**

    Copy `.configuration/.env.example` into a new `.configuration/.env`, and adjust the environment variables accordingly:
    
    - `SLACK_BOT_TOKEN`: Your Slack bot token (This is the Bot User OAuth Token, it should start with 'xoxb').
    - `SLACK_APP_TOKEN`: Your Slack application token (This is the App-Level Token, it should start with 'xapp').
    - `OPENAI_API_KEY`: Your OpenAI API key.
    - `SIGNING_SECRET`: Your Signing secret to verify Slack requests (from your Slack App Credentials).
    - `DALLE_MODEL`: The OpenAI DALL-E-3 model.
    - `CHATGPT_MODEL`: The OpenAI ChatGPT-4 model.
    - `GEMINI_MODEL`: The Gemini model.
    - `GOOGLE_API_KEY`: The Google Gemini API key.

## 🚀 Deployment
Ensure you have Python (3.x), pip, and poetry installed. To deploy Geppetto:

- Clone the repository and navigate to its directory.
- Install dependencies using `poetry install`.
- Launch the application with `poetry run geppetto`.

## 🐳 Docker Deployment
With Docker and Docker Compose ready:

- Rename `docker-compose.example.yml` to `docker-compose.yml` and update your config folder location.
- Adjust configuration values in `config/.env`.
- Execute `docker compose` build followed by `docker compose up -d`.

## 🧪 Testing
Run the following from the root directory to execute tests:

- `python -m unittest` for standard testing.
- `python -m unittest -v` for verbose output.

## 🌐 About DeepTechia
We are [DeepTechia](https://deeptechia.io/), where the future of technology meets today’s business needs. As pioneers in the digital realm, we’ve made it our mission to bridge the gap between innovation and practicality, ensuring that businesses not only survive but thrive in an ever-evolving technological landscape.

Born from a passion for cutting-edge technology and a vision for a digitally integrated future, DeepTechia was established to be more than just a tech consultancy. We are visionaries, strategists, and implementers, dedicated to pushing the boundaries of what’s possible while ensuring real-world applicability.

Over the years, we’ve had the privilege of partnering with over 500 companies from a wide range of industries, guiding them through the intricate maze of digital transformation.

At DeepTechia, we believe in a future where technology enhances every facet of business operations, from efficiency and growth to innovation and customer engagement. Our commitment is unwavering: to provide solutions that are forward-thinking yet grounded, innovative yet practical.

We’re not just your tech consultants; we’re your partners in crafting a digital future that’s bright, secure, and boundless.

## 📜 License
Geppetto is licensed and distributed under the AGPLv3 license. [Contact us](https://deeptechia.io/contact/) if you're looking for an exception to the terms.
