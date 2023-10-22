import os
import smtplib
import ssl
from typing import Optional

import requests

import rcmt.filter
from rcmt import Context, Task


class CheckAPI(rcmt.filter.Base):
    def filter(self, ctx: Context) -> bool:
        """Read a token from an environment variable and use it to call an API."""
        repo_name = ctx.repo.full_name
        # Read token from environment variable
        token = os.getenv("TOKEN")
        bearer = f"Bearer {token}"
        response = requests.get(
            f"https://example.test/check?repo={repo_name}",
            headers={"Authorization": bearer},
        )
        return response.status_code == 200


class SendMail:
    """Send a mail via SMTP."""

    def __init__(self, client: Optional[smtplib.SMTP] = None):
        self._client: Optional[smtplib.SMTP] = client

    def __call__(self, ctx: Context) -> None:
        client = self._create_client()
        client.sendmail(
            from_addr="from@example.test",
            to_addrs=["to@example.test"],
            msg="pull request created",
        )

    def _create_client(self) -> smtplib.SMTP:
        """Create the SMTP only client once to avoid connection churn.
        Read connection details and credentials from environment variables."""
        if self._client is not None:
            return self._client

        self._client = smtplib.SMTP_SSL(
            host=os.getenv("MAIL_HOST", ""),
            port=int(os.getenv("MAIL_PORT", "")),
            context=ssl.create_default_context(),
        )
        self._client.login(
            user=os.getenv("MAIL_USERNAME", ""), password=os.getenv("MAIL_PASSWORD", "")
        )
        return self._client


with Task("custom-configuration") as task:
    task.add_filter(CheckAPI())
    task.on_pr_created(SendMail())
    # Add actions...
