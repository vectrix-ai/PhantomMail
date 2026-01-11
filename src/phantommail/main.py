"""PhantomMail main entry point with interactive terminal menu."""

import asyncio
import os
import sys

from dotenv import load_dotenv

from phantommail.cli.menu import InteractiveMenu, MenuSelection
from phantommail.cli.runner import EmailRunner
from phantommail.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)


async def send_emails(selection: MenuSelection, sender_email: str):
    """Send emails based on menu selection."""
    runner = EmailRunner(sender_email)
    results = await runner.run(selection)
    runner.print_summary(results)


def main():
    """Run PhantomMail CLI."""
    print("\nPhantomMail - Fake Email Generator\n")

    # Validate environment
    sender_email = os.environ.get("SENDER_EMAIL")
    if not sender_email:
        print("Error: SENDER_EMAIL environment variable not set.")
        print("Please set it in your .env file or environment.")
        sys.exit(1)

    resend_key = os.environ.get("RESEND_API_KEY")
    if not resend_key:
        print("Error: RESEND_API_KEY environment variable not set.")
        print("Please set it in your .env file or environment.")
        sys.exit(1)

    # Run interactive menu (synchronous - before async context)
    menu = InteractiveMenu()
    try:
        selection = menu.run()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)

    if selection is None:
        print("\nOperation cancelled.")
        return

    # Execute email sending (async)
    try:
        asyncio.run(send_emails(selection, sender_email))
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
