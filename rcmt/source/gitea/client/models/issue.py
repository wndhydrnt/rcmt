# coding: utf-8

"""
    Gitea API.

    This documentation describes the Gitea API.  # noqa: E501

    The version of the OpenAPI document: 1.18.0+1
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from rcmt.source.gitea.client.configuration import Configuration


class Issue(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'assignee': 'User',
        'assignees': 'list[User]',
        'body': 'str',
        'closed_at': 'datetime',
        'comments': 'int',
        'created_at': 'datetime',
        'due_date': 'datetime',
        'html_url': 'str',
        'id': 'int',
        'is_locked': 'bool',
        'labels': 'list[Label]',
        'milestone': 'Milestone',
        'number': 'int',
        'original_author': 'str',
        'original_author_id': 'int',
        'pull_request': 'PullRequestMeta',
        'ref': 'str',
        'repository': 'RepositoryMeta',
        'state': 'str',
        'title': 'str',
        'updated_at': 'datetime',
        'url': 'str',
        'user': 'User'
    }

    attribute_map = {
        'assignee': 'assignee',
        'assignees': 'assignees',
        'body': 'body',
        'closed_at': 'closed_at',
        'comments': 'comments',
        'created_at': 'created_at',
        'due_date': 'due_date',
        'html_url': 'html_url',
        'id': 'id',
        'is_locked': 'is_locked',
        'labels': 'labels',
        'milestone': 'milestone',
        'number': 'number',
        'original_author': 'original_author',
        'original_author_id': 'original_author_id',
        'pull_request': 'pull_request',
        'ref': 'ref',
        'repository': 'repository',
        'state': 'state',
        'title': 'title',
        'updated_at': 'updated_at',
        'url': 'url',
        'user': 'user'
    }

    def __init__(self, assignee=None, assignees=None, body=None, closed_at=None, comments=None, created_at=None, due_date=None, html_url=None, id=None, is_locked=None, labels=None, milestone=None, number=None, original_author=None, original_author_id=None, pull_request=None, ref=None, repository=None, state=None, title=None, updated_at=None, url=None, user=None, local_vars_configuration=None):  # noqa: E501
        """Issue - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._assignee = None
        self._assignees = None
        self._body = None
        self._closed_at = None
        self._comments = None
        self._created_at = None
        self._due_date = None
        self._html_url = None
        self._id = None
        self._is_locked = None
        self._labels = None
        self._milestone = None
        self._number = None
        self._original_author = None
        self._original_author_id = None
        self._pull_request = None
        self._ref = None
        self._repository = None
        self._state = None
        self._title = None
        self._updated_at = None
        self._url = None
        self._user = None
        self.discriminator = None

        if assignee is not None:
            self.assignee = assignee
        if assignees is not None:
            self.assignees = assignees
        if body is not None:
            self.body = body
        if closed_at is not None:
            self.closed_at = closed_at
        if comments is not None:
            self.comments = comments
        if created_at is not None:
            self.created_at = created_at
        if due_date is not None:
            self.due_date = due_date
        if html_url is not None:
            self.html_url = html_url
        if id is not None:
            self.id = id
        if is_locked is not None:
            self.is_locked = is_locked
        if labels is not None:
            self.labels = labels
        if milestone is not None:
            self.milestone = milestone
        if number is not None:
            self.number = number
        if original_author is not None:
            self.original_author = original_author
        if original_author_id is not None:
            self.original_author_id = original_author_id
        if pull_request is not None:
            self.pull_request = pull_request
        if ref is not None:
            self.ref = ref
        if repository is not None:
            self.repository = repository
        if state is not None:
            self.state = state
        if title is not None:
            self.title = title
        if updated_at is not None:
            self.updated_at = updated_at
        if url is not None:
            self.url = url
        if user is not None:
            self.user = user

    @property
    def assignee(self):
        """Gets the assignee of this Issue.  # noqa: E501


        :return: The assignee of this Issue.  # noqa: E501
        :rtype: User
        """
        return self._assignee

    @assignee.setter
    def assignee(self, assignee):
        """Sets the assignee of this Issue.


        :param assignee: The assignee of this Issue.  # noqa: E501
        :type assignee: User
        """

        self._assignee = assignee

    @property
    def assignees(self):
        """Gets the assignees of this Issue.  # noqa: E501


        :return: The assignees of this Issue.  # noqa: E501
        :rtype: list[User]
        """
        return self._assignees

    @assignees.setter
    def assignees(self, assignees):
        """Sets the assignees of this Issue.


        :param assignees: The assignees of this Issue.  # noqa: E501
        :type assignees: list[User]
        """

        self._assignees = assignees

    @property
    def body(self):
        """Gets the body of this Issue.  # noqa: E501


        :return: The body of this Issue.  # noqa: E501
        :rtype: str
        """
        return self._body

    @body.setter
    def body(self, body):
        """Sets the body of this Issue.


        :param body: The body of this Issue.  # noqa: E501
        :type body: str
        """

        self._body = body

    @property
    def closed_at(self):
        """Gets the closed_at of this Issue.  # noqa: E501


        :return: The closed_at of this Issue.  # noqa: E501
        :rtype: datetime
        """
        return self._closed_at

    @closed_at.setter
    def closed_at(self, closed_at):
        """Sets the closed_at of this Issue.


        :param closed_at: The closed_at of this Issue.  # noqa: E501
        :type closed_at: datetime
        """

        self._closed_at = closed_at

    @property
    def comments(self):
        """Gets the comments of this Issue.  # noqa: E501


        :return: The comments of this Issue.  # noqa: E501
        :rtype: int
        """
        return self._comments

    @comments.setter
    def comments(self, comments):
        """Sets the comments of this Issue.


        :param comments: The comments of this Issue.  # noqa: E501
        :type comments: int
        """

        self._comments = comments

    @property
    def created_at(self):
        """Gets the created_at of this Issue.  # noqa: E501


        :return: The created_at of this Issue.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this Issue.


        :param created_at: The created_at of this Issue.  # noqa: E501
        :type created_at: datetime
        """

        self._created_at = created_at

    @property
    def due_date(self):
        """Gets the due_date of this Issue.  # noqa: E501


        :return: The due_date of this Issue.  # noqa: E501
        :rtype: datetime
        """
        return self._due_date

    @due_date.setter
    def due_date(self, due_date):
        """Sets the due_date of this Issue.


        :param due_date: The due_date of this Issue.  # noqa: E501
        :type due_date: datetime
        """

        self._due_date = due_date

    @property
    def html_url(self):
        """Gets the html_url of this Issue.  # noqa: E501


        :return: The html_url of this Issue.  # noqa: E501
        :rtype: str
        """
        return self._html_url

    @html_url.setter
    def html_url(self, html_url):
        """Sets the html_url of this Issue.


        :param html_url: The html_url of this Issue.  # noqa: E501
        :type html_url: str
        """

        self._html_url = html_url

    @property
    def id(self):
        """Gets the id of this Issue.  # noqa: E501


        :return: The id of this Issue.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Issue.


        :param id: The id of this Issue.  # noqa: E501
        :type id: int
        """

        self._id = id

    @property
    def is_locked(self):
        """Gets the is_locked of this Issue.  # noqa: E501


        :return: The is_locked of this Issue.  # noqa: E501
        :rtype: bool
        """
        return self._is_locked

    @is_locked.setter
    def is_locked(self, is_locked):
        """Sets the is_locked of this Issue.


        :param is_locked: The is_locked of this Issue.  # noqa: E501
        :type is_locked: bool
        """

        self._is_locked = is_locked

    @property
    def labels(self):
        """Gets the labels of this Issue.  # noqa: E501


        :return: The labels of this Issue.  # noqa: E501
        :rtype: list[Label]
        """
        return self._labels

    @labels.setter
    def labels(self, labels):
        """Sets the labels of this Issue.


        :param labels: The labels of this Issue.  # noqa: E501
        :type labels: list[Label]
        """

        self._labels = labels

    @property
    def milestone(self):
        """Gets the milestone of this Issue.  # noqa: E501


        :return: The milestone of this Issue.  # noqa: E501
        :rtype: Milestone
        """
        return self._milestone

    @milestone.setter
    def milestone(self, milestone):
        """Sets the milestone of this Issue.


        :param milestone: The milestone of this Issue.  # noqa: E501
        :type milestone: Milestone
        """

        self._milestone = milestone

    @property
    def number(self):
        """Gets the number of this Issue.  # noqa: E501


        :return: The number of this Issue.  # noqa: E501
        :rtype: int
        """
        return self._number

    @number.setter
    def number(self, number):
        """Sets the number of this Issue.


        :param number: The number of this Issue.  # noqa: E501
        :type number: int
        """

        self._number = number

    @property
    def original_author(self):
        """Gets the original_author of this Issue.  # noqa: E501


        :return: The original_author of this Issue.  # noqa: E501
        :rtype: str
        """
        return self._original_author

    @original_author.setter
    def original_author(self, original_author):
        """Sets the original_author of this Issue.


        :param original_author: The original_author of this Issue.  # noqa: E501
        :type original_author: str
        """

        self._original_author = original_author

    @property
    def original_author_id(self):
        """Gets the original_author_id of this Issue.  # noqa: E501


        :return: The original_author_id of this Issue.  # noqa: E501
        :rtype: int
        """
        return self._original_author_id

    @original_author_id.setter
    def original_author_id(self, original_author_id):
        """Sets the original_author_id of this Issue.


        :param original_author_id: The original_author_id of this Issue.  # noqa: E501
        :type original_author_id: int
        """

        self._original_author_id = original_author_id

    @property
    def pull_request(self):
        """Gets the pull_request of this Issue.  # noqa: E501


        :return: The pull_request of this Issue.  # noqa: E501
        :rtype: PullRequestMeta
        """
        return self._pull_request

    @pull_request.setter
    def pull_request(self, pull_request):
        """Sets the pull_request of this Issue.


        :param pull_request: The pull_request of this Issue.  # noqa: E501
        :type pull_request: PullRequestMeta
        """

        self._pull_request = pull_request

    @property
    def ref(self):
        """Gets the ref of this Issue.  # noqa: E501


        :return: The ref of this Issue.  # noqa: E501
        :rtype: str
        """
        return self._ref

    @ref.setter
    def ref(self, ref):
        """Sets the ref of this Issue.


        :param ref: The ref of this Issue.  # noqa: E501
        :type ref: str
        """

        self._ref = ref

    @property
    def repository(self):
        """Gets the repository of this Issue.  # noqa: E501


        :return: The repository of this Issue.  # noqa: E501
        :rtype: RepositoryMeta
        """
        return self._repository

    @repository.setter
    def repository(self, repository):
        """Sets the repository of this Issue.


        :param repository: The repository of this Issue.  # noqa: E501
        :type repository: RepositoryMeta
        """

        self._repository = repository

    @property
    def state(self):
        """Gets the state of this Issue.  # noqa: E501

        StateType issue state type  # noqa: E501

        :return: The state of this Issue.  # noqa: E501
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this Issue.

        StateType issue state type  # noqa: E501

        :param state: The state of this Issue.  # noqa: E501
        :type state: str
        """

        self._state = state

    @property
    def title(self):
        """Gets the title of this Issue.  # noqa: E501


        :return: The title of this Issue.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this Issue.


        :param title: The title of this Issue.  # noqa: E501
        :type title: str
        """

        self._title = title

    @property
    def updated_at(self):
        """Gets the updated_at of this Issue.  # noqa: E501


        :return: The updated_at of this Issue.  # noqa: E501
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this Issue.


        :param updated_at: The updated_at of this Issue.  # noqa: E501
        :type updated_at: datetime
        """

        self._updated_at = updated_at

    @property
    def url(self):
        """Gets the url of this Issue.  # noqa: E501


        :return: The url of this Issue.  # noqa: E501
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url):
        """Sets the url of this Issue.


        :param url: The url of this Issue.  # noqa: E501
        :type url: str
        """

        self._url = url

    @property
    def user(self):
        """Gets the user of this Issue.  # noqa: E501


        :return: The user of this Issue.  # noqa: E501
        :rtype: User
        """
        return self._user

    @user.setter
    def user(self, user):
        """Sets the user of this Issue.


        :param user: The user of this Issue.  # noqa: E501
        :type user: User
        """

        self._user = user

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Issue):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Issue):
            return True

        return self.to_dict() != other.to_dict()
