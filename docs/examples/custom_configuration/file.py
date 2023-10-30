import smtplib
import ssl
from typing import Optional

import requests

from rcmt import Context, Task, context, register_task


class API:
    def __init__(self):
        self.session = requests.Session()

    def check(self, ctx: Context) -> bool:
        """Read a token from an environment variable and use it to call an API."""
        repo_name = ctx.repo.full_name
        # Read token from section "custom" of the configuration file
        token = ctx.custom_config["token"]
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

        # Get custom configuration
        mail_cfg: dict = ctx.custom_config.get("mail", {})
        self._client = smtplib.SMTP_SSL(
            host=mail_cfg["host"],
            port=mail_cfg["port"],
            context=ssl.create_default_context(),
        )
        self._client.login(user=mail_cfg["username"], password=mail_cfg["password"])
        return self._client


class CustomConfigurationRCMTConfig(Task):
    def __init__(self, check: API, mail: SendMail):
        self.check = check
        self.mail = mail

    def filter(self, ctx: context.Context) -> bool:
        # Call a custom API to determine if the Task should modify a repository.
        return self.check.check(ctx=ctx)

    def apply(self, ctx: context.Context) -> None:
        """Whatever modifications need to be done."""

    def on_pr_created(self, ctx: context.Context) -> None:
        # Send an e-mail on creation of a pull request.
        self.mail.send(ctx=ctx)


register_task(CustomConfigurationRCMTConfig(check=API(), mail=SendMail()))
