import asyncio
import os

from dotenv import load_dotenv

from phantommail.graphs.graph import graph
from phantommail.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)


async def main():
    """Mail function that sends an email to the recipient."""
    recipient = input("Please enter the recipient's email address: ")
    config = {"configurable": {"sender": os.environ["SENDER_EMAIL"]}}
    response = await graph.ainvoke({"recipients": [recipient]}, config=config)
    return response


if __name__ == "__main__":
    asyncio.run(main())
