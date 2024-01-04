# Geppetto

![https://img.shields.io/badge/license-MIT-green](https://img.shields.io/badge/license-MIT-green)

<p align="center">
  <img src="./assets/GeppettoMini.png" alt="Geppetto" center/>
</p>

Geppetto is a Slack bot that integrates with OpenAI's and DALL-E-3 models. 

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
   - Only authorized users can interact with the application. Check with the administrator for permissions.

## Configuration

Before running the application, make sure to set the following environment variables in a `.env` file:

- `SLACK_BOT_TOKEN`: Slack bot token.
- `SLACK_APP_TOKEN`: Slack application token.
- `OPENAI_API_KEY`: OpenAI API key.
- `SIGNING_SECRET`: Signing secret to verify Slack requests.
- `DALLE_MODEL`: OpenAI's DALL-E-3 model.
- `CHATGPT_MODEL`: OpenAI's ChatGPT-4 model.

## Execution

1. Install dependencies with `pip install -r requirements.txt`.
2. Run the application with `python script_name.py`.

Enjoy interacting with ChatGPT-4 and DALL-E-3 on Slack!


## About CoinFabrik

We - [CoinFabrik](https://www.coinfabrik.com/) - are a research and development company specialized in Web3, with a strong background in cybersecurity. Founded in 2014, we have worked on over 180 blockchain-related projects, EVM based and also for Solana, Algorand, and Polkadot. Beyond development, we offer security audits through a dedicated in-house team of senior cybersecurity professionals, currently working on code in Substrate, Solidity, Clarity, Rust, TEAL and Stellar Soroban.

Our team has an academic background in computer science and mathematics, with work experience focused on cybersecurity and software development, including academic publications, patents turned into products, and conference presentations. Furthermore, we have an ongoing collaboration on knowledge transfer and open-source projects with the University of Buenos Aires.

## License

Geppetto is licensed and distributed under a MIT license. [Contact us](https://www.coinfabrik.com/) if you're looking for an exception to the terms.
