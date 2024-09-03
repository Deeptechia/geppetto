
<img src="./assets/GeppettoMini.png" alt="Geppetto Logo"/>

# Geppetto

![License: AGPLv3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg) 
![Geppetto Tests](https://github.com/Deeptechia/geppetto/actions/workflows/tests-python.yml/badge.svg)

[DeepTechia](https://deeptechia.io/), is proud to introduce Geppetto, a versatile Slack bot that seamlessly integrates with various AI models, empowering your team with the power of cutting-edge AI technology 🚀

## ⭐️ Key Features

- 🔀 **Multi-Model Support:** Toggle effortlessly between AI models like ChatGPT, Claude and Gemini to suit your specific requirements. ChatGPT model gpt4-turbo is set as the default model.
- 🔑 **Access for All:** Provide access for everyone in slack without requiring any additional payment or configuration per user.
- 💬 **Streamlined Communication:** Initiate dynamic conversation threads by directly messaging Geppetto.
- ➡️ **Advanced LLM Control:** Manage multiple AI models with the advanced LLM controller component.
- 🔧 **Effortless Setup:** Enjoy a smooth setup experience powered by Docker 🐳.
- 🎨 **Creative Image Generation:** Unleash the power of DALL-E-3 to generate innovative images directly within your Slack conversations.

## 🚀 **Demo**

![Geppetto](/assets/Geppetto_demo.png)
![Geppetto](/assets/Geppetto_demo2.png)

## 👨‍💻 Usage Guidelines

### 📩 Direct Messages

- Directly messaging the bot does not require mentioning it with "@".
- Each direct message generates a conversation thread.

### 💬 Slack Channels

- Invoke Geppetto in channel discussions by mentioning it with "@".

### 🔒 Allowed Users

- Access is granted only to users listed in the [allowed users configuration file](/config/allowed-slack-ids.json).

## 🔀 Switching AI Models

- To switch between ChatGPT, Gemini and Claude include the following commands in your message:
  - `llm_openai` to use ChatGPT
  - `llm_gemini` to use Gemini
  - `llm_claude` to use Claude

## 📚 Listing all available AI models

- Only type `llms` in your message.

## 🛠️ Setup and Configuration

### 🔧 Slack App Configuration

1. **Modify App**:
   - **Edit `config/manifest-dev.yaml`**: Adjust fields under `display_information` and `bot_user` to tailor Geppetto for your needs.
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

    Copy `config/.env.example` into a new `config/.env`, and adjust the environment variables accordingly:

    - `SLACK_BOT_TOKEN`: Your Slack bot token (This is the Bot User OAuth Token, it should start with 'xoxb').
    - `SLACK_APP_TOKEN`: Your Slack application token (This is the App-Level Token, it should start with 'xapp').
    - `OPENAI_API_KEY`: Your OpenAI API key.
    - `SIGNING_SECRET`: Your Signing secret to verify Slack requests (from your Slack App Credentials).
    - `DALLE_MODEL`: The OpenAI DALL-E model.
    - `CHATGPT_MODEL`: The OpenAI ChatGPT model.
    - `GEMINI_MODEL`: The Gemini model.
    - `GOOGLE_API_KEY`: The Google Gemini API key.
    - `CLAUDE_MODEL`: The Claude model.
    - `CLAUDE_API_KEY`: The Anthropic Claude API key.

## 🚀 Deployment

Ensure you have Python (3.x), pip, and poetry installed. To deploy Geppetto:

- Clone the repository and navigate to its directory.
- Install dependencies using `poetry install`.
- Launch the application with `poetry run geppetto`.

## 🐳 Docker Deployment

With Docker and Docker Compose ready:

- Rename `docker-compose.example.yml` to `docker-compose.yml` and update your config folder location.
- Adjust configuration values in `config/.env`.
- Execute `docker compose build` followed by `docker compose up -d`.

We published our docker container for download on Dockerhub:
https://hub.docker.com/r/deeptechia/geppetto

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
