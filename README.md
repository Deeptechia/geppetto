# Geppetto

![https://img.shields.io/badge/license-MIT-green](https://img.shields.io/badge/license-MIT-green)

<p align="center">
  <img src="./assets/GeppettoMini.png" alt="Geppetto" center/>
</p>

Geppetto is a Slack bot for teams to easily interact with ChatGPT. It integrates with OpenAI's and DALL-E-3 models  This project is brought to you by [CoinFabrik](https://www.coinfabrik.com) a company specialized in cybersecurity and decentralized technologies. We recommend to read our [blog](https://www.coinfabrik.com/blog/) and follow us: [Twitter/X](https://twitter.com/coinfabrik), and [LinkedIn](https://www.linkedin.com/company/coinfabrik).

## Features

1. **Initial Greeting:**
   - When you send a message containing the word "hello," the application responds with a greeting.

2. **Interaction with ChatGPT-4:**
   - You can send direct messages to the application and receive responses from ChatGPT-4.
   - Each message generates a conversation thread, and the application uses the message history to formulate coherent responses.

3. **Image Generation with DALL-E-3:**
   - If you include the word "dalle" in your message, the application uses DALL-E-3 to generate an image based on the message.

## Usage Rules

- **Direct Messages:**
   - It is not necessary to mention the application with "@" in direct messages.
   - Each direct message generates a conversation thread.

- **Slack Channels:**
   - You must mention the application with "@" to interact in channels.
   - Include the word "dalle" in your message to request image generation with DALL-E-3.

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
1. Under the *App Credentials* section, save the following:
   - **Client Secret**: This will be our `SLACK_BOT_TOKEN`.
   - **Signing Secret**.
2. In the *App-Level Tokens* section:
   - Click on *Generate Tokens and Scopes*.
   - Set a Token Name and assign the scope to `connections write`.
   - Generate and save the **App-Level Token** for later use (this will be our `SLACK_APP_TOKEN`).

#### Reinstall Workspace
Finally, in the *Basic Information* section, click on *Reinstall Workspace*. This action requires approval from an owner of your Slack workspace to consolidate the changes.


#### Enviroment Configuration

Before running the application, copy the `.configuration/.env.example` file into a new `.configuration/.env` file. Modify the following environment variables in this file:

- `SLACK_BOT_TOKEN`: Slack bot token. This is the `Client Secret` from your slack App Credentials.
- `SLACK_APP_TOKEN`: Slack application token. This is the `App-Level Token` from your slack App Credentials
- `OPENAI_API_KEY`: OpenAI API key.
- `SIGNING_SECRET`: Signing secret to verify Slack requests. This is the `Signing Secret` your slack App Credentials.
- `DALLE_MODEL`: OpenAI's DALL-E-3 model.
- `CHATGPT_MODEL`: OpenAI's ChatGPT-4 model.

## Execution

1. Install dependencies with `pip install -r requirements.txt`.
2. Run the application with `python script_name.py`.

Enjoy interacting with ChatGPT-4 and DALL-E-3 on Slack!


## About CoinFabrik

[CoinFabrik](https://www.coinfabrik.com/) is a research and development company specialized in Web3, with a strong background in cybersecurity. Founded in 2014, we have worked on over 250 decentralization projects, EVM based as well as Solana, Algorand, and Polkadot, among others. Beyond development, we offer security audits through a dedicated in-house team of senior cybersecurity professionals, currently working on code in Substrate, Solidity, Clarity, Rust, TEAL and Stellar Soroban.

Our team has an academic background in computer science, software engineering, and mathematics, including academic publications, patents turned into products, and conference presentations. Furthermore, we research along universities around the world. For example, we work with Cornell, UCLA, École Polytechnique in Paris and have an ongoing collaboration on knowledge transfer and open-source projects with the University of Buenos Aires, Argentina. Last, but not least, we have a great management and people experience team with strong experience in the field.

## License

Geppetto is licensed and distributed under a MIT license. [Contact us](https://www.coinfabrik.com/#contact-us) if you're looking for an exception to the terms.
