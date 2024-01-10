# Geppetto

![License: MIT](https://img.shields.io/badge/license-MIT-green)

<p align="center">
  <img src="./assets/GeppettoMini.png" alt="Geppetto Logo"/>
</p>

Geppetto is a Slack bot for teams to easily interact with ChatGPT. It integrates with OpenAI's ChatGPT-4 and DALL-E-3 models. This project is brought to you by [CoinFabrik](https://www.coinfabrik.com), a company specialized in cybersecurity and decentralized technologies. We recommend reading our [blog](https://www.coinfabrik.com/blog/) and following us on [Twitter](https://twitter.com/coinfabrik) and [LinkedIn](https://www.linkedin.com/company/coinfabrik).

## Features

1. **Interaction with ChatGPT-4:**
   - You can send direct messages to the application and receive responses from ChatGPT-4.
   - Each message generates a conversation thread, and the application uses the message history to formulate coherent responses.

2. **Image Generation with DALL-E-3:**
   - The application uses DALL-E-3 to generate an image based on the message.

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

Follow these steps to deploy Geppetto:

1. Download the repository and open your terminal.
2. Navigate to the repository directory and install dependencies with `pip install .`.
3. Run the application by entering `geppetto` in the terminal.

Enjoy interacting with ChatGPT-4 and DALL-E-3 on Slack!

## About CoinFabrik

[CoinFabrik](https://www.coinfabrik.com/) is a research and development company specialized in Web3, with a strong background in cybersecurity. Founded in 2014, we have worked on over 250 decentralization projects, including EVM-based and other platforms like Solana, Algorand, and Polkadot. Beyond development, we offer security audits through a dedicated in-house team of senior cybersecurity professionals, working on code in languages such as Substrate, Solidity, Clarity, Rust, TEAL, and Stellar Soroban.

Our team has an academic background in computer science, software engineering, and mathematics, with accomplishments including academic publications, patents turned into products, and conference presentations. We actively research in collaboration with universities worldwide, such as Cornell, UCLA, and École Polytechnique in Paris, and maintain an ongoing collaboration on knowledge transfer and open-source projects with the University of Buenos Aires, Argentina. Our management and people experience team has extensive expertise in the field.

## License

Geppetto is licensed and distributed under the MIT license. [Contact us](https://www.coinfabrik.com/#contact-us) if you're looking for an exception to the terms.
