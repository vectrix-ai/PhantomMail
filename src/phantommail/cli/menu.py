"""Interactive terminal menu for PhantomMail."""

import re
from dataclasses import dataclass

import questionary
from questionary import Choice, Style

# Custom style for the menu
custom_style = Style(
    [
        ("qmark", "fg:yellow bold"),
        ("question", "bold"),
        ("answer", "fg:green bold"),
        ("pointer", "fg:yellow bold"),
        ("highlighted", "fg:yellow bold"),
        ("selected", "fg:green"),
    ]
)

# Available email types matching GraphNodes.email_types()
EMAIL_TYPES = [
    ("order", "Transport order with pickup/delivery details"),
    ("declaration", "Customs/import declaration emails"),
    ("question", "General transport-related questions"),
    ("complaint", "Customer complaint emails"),
    ("price_request", "Price negotiation/inquiry emails"),
    ("waiting_costs", "Dispute emails for waiting charges"),
    ("update_order", "Request updates on existing orders"),
    ("random", "Random promotional emails"),
]


@dataclass
class MenuSelection:
    """Data class holding user's menu selections."""

    email_type: str  # Single type or "all_random"
    count: int
    recipients: list[str]


class InteractiveMenu:
    """Interactive terminal menu for PhantomMail configuration."""

    def __init__(self):
        """Initialize the interactive menu."""
        self.email_type_choices = [
            Choice(title=f"{name}: {desc}", value=name) for name, desc in EMAIL_TYPES
        ]
        # Add "all types randomly" option at the top
        self.email_type_choices.insert(
            0,
            Choice(
                title="all_random: Random type for each email",
                value="all_random",
            ),
        )

    def run(self) -> MenuSelection | None:
        """Run the interactive menu and return user selections.

        Returns:
            MenuSelection with user choices, or None if cancelled.

        """
        # Step 1: Select email type
        email_type = self._select_email_type()
        if email_type is None:
            return None

        # Step 2: Select count
        count = self._select_count()
        if count is None:
            return None

        # Step 3: Enter recipients
        recipients = self._enter_recipients()
        if not recipients:
            return None

        # Step 4: Confirm
        confirmed = self._confirm_selection(email_type, count, recipients)
        if not confirmed:
            return None

        return MenuSelection(
            email_type=email_type,
            count=count,
            recipients=recipients,
        )

    def _select_email_type(self) -> str | None:
        """Prompt user to select email type."""
        return questionary.select(
            "Select email type to generate:",
            choices=self.email_type_choices,
            style=custom_style,
        ).ask()

    def _select_count(self) -> int | None:
        """Prompt user to enter number of emails."""
        result = questionary.text(
            "How many emails to send?",
            default="1",
            validate=lambda x: x.isdigit()
            and int(x) > 0
            or "Please enter a positive number",
            style=custom_style,
        ).ask()
        return int(result) if result else None

    def _enter_recipients(self) -> list[str]:
        """Prompt user to enter recipient email addresses."""
        result = questionary.text(
            "Enter recipient email address(es) (comma-separated for multiple):",
            validate=self._validate_emails,
            style=custom_style,
        ).ask()

        if not result:
            return []

        # Parse comma-separated emails
        return [email.strip() for email in result.split(",") if email.strip()]

    def _validate_emails(self, value: str) -> bool | str:
        """Validate email addresses."""
        if not value or not value.strip():
            return "Please enter at least one email address"

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        emails = [e.strip() for e in value.split(",") if e.strip()]

        for email in emails:
            if not re.match(email_pattern, email):
                return f"Invalid email format: {email}"

        return True

    def _confirm_selection(
        self,
        email_type: str,
        count: int,
        recipients: list[str],
    ) -> bool:
        """Show confirmation prompt."""
        type_display = (
            "random (different type each email)"
            if email_type == "all_random"
            else email_type
        )

        print("\nConfiguration Summary:")
        print(f"  Email Type: {type_display}")
        print(f"  Count: {count} email(s)")
        print(f"  Recipients: {', '.join(recipients)}\n")

        return questionary.confirm(
            "Proceed with sending?",
            default=True,
            style=custom_style,
        ).ask()
