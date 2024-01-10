# Geppetto

![https://img.shields.io/badge/license-MIT-green](https://img.shields.io/badge/license-MIT-green)

<p align="center">
  <img src="./assets/GeppettoMini.png" alt="Geppetto" center/>
</p>

Geppetto is a Slack bot for teams to easily interact with ChatGPT. It integrates with OpenAI's and DALL-E-3 models  This project is brought to you by [CoinFabrik](https://www.coinfabrik.com) a company specialized in cybersecurity and decentralized technologies. We recommend to read our [blog](https://www.coinfabrik.com/blog/) and follow us: [Twitter/X](https://twitter.com/coinfabrik), and [LinkedIn](https://www.linkedin.com/company/coinfabrik).

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

[CoinFabrik](https://www.coinfabrik.com/) is a research and development company specialized in Web3, with a strong background in cybersecurity. Founded in 2014, we have worked on over 250 decentralization projects, EVM based as well as Solana, Algorand, and Polkadot, among others. Beyond development, we offer security audits through a dedicated in-house team of senior cybersecurity professionals, currently working on code in Substrate, Solidity, Clarity, Rust, TEAL and Stellar Soroban.

Our team has an academic background in computer science, software engineering, and mathematics, including academic publications, patents turned into products, and conference presentations. Furthermore, we research along universities around the world. For example, we work with Cornell, UCLA, École Polytechnique in Paris and have an ongoing collaboration on knowledge transfer and open-source projects with the University of Buenos Aires, Argentina. Last, but not least, we have a great management and people experience team with strong experience in the field.

## License

Geppetto is licensed and distributed under a MIT license. [Contact us](https://www.coinfabrik.com/#contact-us) if you're looking for an exception to the terms.
