import os
import smtplib
import ssl
from typing import Optional

import requests

from rcmt import Context, Task, register_task


class API:
    def __init__(self):
        self.session = requests.Session()

    def check(self, ctx: Context) -> bool:
        """Read a token from an environment variable and use it to call an API."""
        repo_name = ctx.repo.full_name
        # Read token from environment variable
        token = os.getenv("TOKEN")
        bearer = f"Bearer {token}"
        response = self.session.get(
            f"https://example.test/check?repo={repo_name}",
            headers={"Authorization": bearer},
        )
        return response.status_code == 200


class SendMail:
    """Send a mail via SMTP."""

    def __init__(self, client: Optional[smtplib.SMTP] = None):
        self._client: Optional[smtplib.SMTP] = client

    def send(self, ctx: Context) -> None:
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

        # Get configuration from environment variables
        self._client = smtplib.SMTP_SSL(
            host=os.getenv("MAIL_HOST", ""),
            port=int(os.getenv("MAIL_PORT", "")),
            context=ssl.create_default_context(),
        )
        self._client.login(
            user=os.getenv("MAIL_USERNAME", ""), password=os.getenv("MAIL_PASSWORD", "")
        )
        return self._client


class CustomConfigurationEnvVars(Task):
    def __init__(self, check: API, mail: SendMail):
        self.check = check
        self.mail = mail

    def filter(self, ctx: Context) -> bool:
        # Call a custom API to determine if the Task should modify a repository.
        return self.check.check(ctx=ctx)

    def apply(self, ctx: Context) -> None:
        """Whatever modifications need to be done."""

    def on_pr_created(self, ctx: Context) -> None:
        # Send an e-mail on creation of a pull request.
        self.mail.send(ctx=ctx)


register_task(CustomConfigurationEnvVars(check=API(), mail=SendMail()))
