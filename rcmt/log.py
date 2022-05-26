from typing import Any, Mapping, MutableMapping


class SecretMasker:
    def __init__(self):
        self.secrets: list[str] = []

    def add_secret(self, s: str) -> None:
        self.secrets.append(s)

    def process_event(
        self, _, __, event_dict: MutableMapping[str, Any]
    ) -> Mapping[str, Any]:
        for k, v in event_dict.items():
            if not isinstance(v, str):
                continue

            for secret in self.secrets:
                if secret in v:
                    event_dict[k] = v.replace(secret, "****")

        return event_dict


SECRET_MASKER = SecretMasker()
