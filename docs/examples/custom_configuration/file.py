import smtplib
import ssl
from typing import Optional

import requests

from rcmt import Context, Task
from rcmt.filter import Base


class CheckAPI(Base):
    def filter(self, ctx: Context) -> bool:
        """Read a token from an environment variable and use it to call an API."""
        repo_name = ctx.repo.full_name
        # Read token from section "custom" of the configuration file
        token = ctx.custom_config["token"]
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
        client = self._create_client(ctx)
        client.sendmail(
            from_addr="from@example.test",
            to_addrs=["to@example.test"],
            msg="pull request created",
        )

    def _create_client(self, ctx: Context) -> smtplib.SMTP:
        """Create the SMTP only client once to avoid connection churn.
        Read connection details and credentials section "custom" of the configuration
        file.
        """
        if self._client is not None:
            return self._client

        # Get custom configuration
        mail_cfg: dict = ctx.custom_config.get("mail", {})
        self._client = smtplib.SMTP_SSL(
            host=mail_cfg["host"],
            port=mail_cfg["port"],
            context=ssl.create_default_context(),
        )
        self._client.login(user=mail_cfg["username"], password=mail_cfg["password"])
        return self._client


with Task("custom-configuration") as task:
    task.add_filter(CheckAPI())
    task.on_pr_created(SendMail())
    # Add actions...
