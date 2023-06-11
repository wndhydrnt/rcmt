from typing import Any
from rcmt.source import Repository


class Event:
    """Event is a data class. Instance of this class is passed to each listeners"""

    def __init__(self):
        pass


class PREvent(Event):
    """PR Event is a data class. Instance of this class is passed to each listeners related to PR"""

    def __init__(self, pr_id=None, pr: Any = {}, repository: Repository = {}):
        self.pr_id = pr_id
        self.pr: Any = pr
        self.repository: Repository = repository


class EventListener:
    def on_pr_created(self, event: PREvent):
        """
        on_pr_created listener is called after pr creation.

        :param event: Event object generate after PR creation.
        :return: None
        """
        pass

    def on_pr_merged(self, event: PREvent):
        """
        on_pr_merged listener is called after the pr is merged.

        :param event: Event object generated after PR merge.
        :return: None
        """
        pass

    def on_pr_closed(self, event: PREvent):
        """
        on_pr_closed listener is called after the pr is closed.

        :param event: Event object generated after PR close.
        :return: None
        """
        pass

    def on_pr_updated(self, event: PREvent):
        """
        on_pr_updated listener is called after pr update.

        :param event: Event object generated after PR update.
        :return: None
        """
        pass
