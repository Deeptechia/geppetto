import asyncio
import logging
import argparse

from geppetto.core.multiplexer import LLMMultiplexer, LLMType
from geppetto.platforms.slack_bot import run_slack_bot
from geppetto.utils import load_config

SLACK_CONFIG_PATH = "config/slack.json"
SLACK_USERS_CONFIG_PATH = "config/allowed-slack-ids.json"
LLM_CONFIG_PATH = "config/llm.json"


async def run_slack(llm_multiplexer: LLMMultiplexer):
    return await run_slack_bot(
        config_path=SLACK_CONFIG_PATH,
        users_path=SLACK_USERS_CONFIG_PATH,
        llm_multiplexer=llm_multiplexer,
    )


async def run_discord(llm_multiplexer: LLMMultiplexer):
    pass


async def run_teams(llm_multiplexer: LLMMultiplexer):
    pass


async def main(platform: str):
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Initialize LLM provider
    # TODO: models should be more dynamic
    llm_config = load_config(LLM_CONFIG_PATH)
    llm_multiplexer = LLMMultiplexer(
        api_keys={
            LLMType.OPENAI: llm_config["OPENAI_API_KEY"],
            LLMType.CLAUDE: llm_config["CLAUDE_API_KEY"],
            LLMType.GEMINI: llm_config["GEMINI_API_KEY"],
        },
        models={
            LLMType.OPENAI: llm_config.get("OPENAI_MODEL", "gpt-4o"),
            LLMType.CLAUDE: llm_config.get(
                "CLAUDE_MODEL", "claude-3-5-sonnet-20240620"
            ),
            LLMType.GEMINI: llm_config.get("GEMINI_MODEL", "gemini-1.5-pro"),
        },
        default_llm=LLMType.OPENAI,
    )

    try:
        match platform:
            case "slack":
                await run_slack(llm_multiplexer)
            case "discord":
                logger.info("Discord is not supported yet")
                await run_discord(llm_multiplexer)
            case "teams":
                logger.info("Teams is not supported yet")
                await run_teams(llm_multiplexer)
            case _:
                logger.error(f"Platform '{platform}' is not supported yet")
                return

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")


def cli():
    parser = argparse.ArgumentParser(
        description="Run Geppetto bot on different platforms"
    )
    parser.add_argument(
        "--platform",
        choices=["slack", "discord", "teams"],
        required=True,
        help="Platform to run the bot on (e.g., slack)",
    )

    args = parser.parse_args()
    asyncio.run(main(args.platform))


if __name__ == "__main__":
    cli()
