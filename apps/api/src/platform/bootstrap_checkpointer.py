import asyncio

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from src.platform.config import get_settings


async def main():
    async with AsyncPostgresSaver.from_conn_string(get_settings().checkpoint_url) as saver:
        await saver.setup()


if __name__ == "__main__":
    asyncio.run(main())
