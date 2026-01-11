"""Email sending runner with progress indication."""

import asyncio
import random

from phantommail.cli.menu import MenuSelection
from phantommail.graphs.graph import graph
from phantommail.logger import setup_logger

logger = setup_logger(__name__, level="INFO")

# Email types for random selection
SELECTABLE_TYPES = [
    "order",
    "declaration",
    "question",
    "complaint",
    "price_request",
    "waiting_costs",
    "update_order",
    "random",
]


class EmailRunner:
    """Orchestrates email generation and sending with progress tracking."""

    def __init__(self, sender_email: str):
        """Initialize the email runner.

        Args:
            sender_email: The sender email address from config.

        """
        self.sender_email = sender_email
        self.config = {"configurable": {"sender": sender_email}}

    async def run(self, selection: MenuSelection) -> dict:
        """Execute email sending based on menu selection.

        Args:
            selection: The user's menu selections.

        Returns:
            Summary dict with success/failure counts.

        """
        results = {
            "total": selection.count,
            "success": 0,
            "failed": 0,
            "errors": [],
        }

        print(f"\nSending {selection.count} email(s)...\n")

        for i in range(selection.count):
            # Determine email type for this iteration
            if selection.email_type == "all_random":
                email_type = random.choice(SELECTABLE_TYPES)
            else:
                email_type = selection.email_type

            # Progress indicator
            progress = f"[{i + 1}/{selection.count}]"
            print(f"{progress} Generating {email_type} email...", end=" ", flush=True)

            try:
                # Invoke the graph
                await graph.ainvoke(
                    {
                        "recipients": selection.recipients,
                        "email_type": email_type,
                    },
                    config=self.config,
                )
                print("Sent!")
                results["success"] += 1

            except Exception as e:
                print(f"Failed: {e}")
                results["failed"] += 1
                results["errors"].append(f"Email {i + 1} ({email_type}): {e!s}")
                logger.error(f"Failed to send email {i + 1}: {e}")

            # Small delay between emails to avoid rate limiting
            if i < selection.count - 1:
                await asyncio.sleep(0.5)

        return results

    @staticmethod
    def print_summary(results: dict) -> None:
        """Print a summary of the sending results.

        Args:
            results: The results dict from run().

        """
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(
            f"Total: {results['total']} | Success: {results['success']} | Failed: {results['failed']}"
        )

        if results["errors"]:
            print("\nErrors:")
            for error in results["errors"]:
                print(f"  - {error}")

        print("=" * 50)
