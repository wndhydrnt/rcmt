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


class DeployKey(object):
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
        'created_at': 'datetime',
        'fingerprint': 'str',
        'id': 'int',
        'key': 'str',
        'key_id': 'int',
        'read_only': 'bool',
        'repository': 'Repository',
        'title': 'str',
        'url': 'str'
    }

    attribute_map = {
        'created_at': 'created_at',
        'fingerprint': 'fingerprint',
        'id': 'id',
        'key': 'key',
        'key_id': 'key_id',
        'read_only': 'read_only',
        'repository': 'repository',
        'title': 'title',
        'url': 'url'
    }

    def __init__(self, created_at=None, fingerprint=None, id=None, key=None, key_id=None, read_only=None, repository=None, title=None, url=None, local_vars_configuration=None):  # noqa: E501
        """DeployKey - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._created_at = None
        self._fingerprint = None
        self._id = None
        self._key = None
        self._key_id = None
        self._read_only = None
        self._repository = None
        self._title = None
        self._url = None
        self.discriminator = None

        if created_at is not None:
            self.created_at = created_at
        if fingerprint is not None:
            self.fingerprint = fingerprint
        if id is not None:
            self.id = id
        if key is not None:
            self.key = key
        if key_id is not None:
            self.key_id = key_id
        if read_only is not None:
            self.read_only = read_only
        if repository is not None:
            self.repository = repository
        if title is not None:
            self.title = title
        if url is not None:
            self.url = url

    @property
    def created_at(self):
        """Gets the created_at of this DeployKey.  # noqa: E501


        :return: The created_at of this DeployKey.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this DeployKey.


        :param created_at: The created_at of this DeployKey.  # noqa: E501
        :type created_at: datetime
        """

        self._created_at = created_at

    @property
    def fingerprint(self):
        """Gets the fingerprint of this DeployKey.  # noqa: E501


        :return: The fingerprint of this DeployKey.  # noqa: E501
        :rtype: str
        """
        return self._fingerprint

    @fingerprint.setter
    def fingerprint(self, fingerprint):
        """Sets the fingerprint of this DeployKey.


        :param fingerprint: The fingerprint of this DeployKey.  # noqa: E501
        :type fingerprint: str
        """

        self._fingerprint = fingerprint

    @property
    def id(self):
        """Gets the id of this DeployKey.  # noqa: E501


        :return: The id of this DeployKey.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this DeployKey.


        :param id: The id of this DeployKey.  # noqa: E501
        :type id: int
        """

        self._id = id

    @property
    def key(self):
        """Gets the key of this DeployKey.  # noqa: E501


        :return: The key of this DeployKey.  # noqa: E501
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this DeployKey.


        :param key: The key of this DeployKey.  # noqa: E501
        :type key: str
        """

        self._key = key

    @property
    def key_id(self):
        """Gets the key_id of this DeployKey.  # noqa: E501


        :return: The key_id of this DeployKey.  # noqa: E501
        :rtype: int
        """
        return self._key_id

    @key_id.setter
    def key_id(self, key_id):
        """Sets the key_id of this DeployKey.


        :param key_id: The key_id of this DeployKey.  # noqa: E501
        :type key_id: int
        """

        self._key_id = key_id

    @property
    def read_only(self):
        """Gets the read_only of this DeployKey.  # noqa: E501


        :return: The read_only of this DeployKey.  # noqa: E501
        :rtype: bool
        """
        return self._read_only

    @read_only.setter
    def read_only(self, read_only):
        """Sets the read_only of this DeployKey.


        :param read_only: The read_only of this DeployKey.  # noqa: E501
        :type read_only: bool
        """

        self._read_only = read_only

    @property
    def repository(self):
        """Gets the repository of this DeployKey.  # noqa: E501


        :return: The repository of this DeployKey.  # noqa: E501
        :rtype: Repository
        """
        return self._repository

    @repository.setter
    def repository(self, repository):
        """Sets the repository of this DeployKey.


        :param repository: The repository of this DeployKey.  # noqa: E501
        :type repository: Repository
        """

        self._repository = repository

    @property
    def title(self):
        """Gets the title of this DeployKey.  # noqa: E501


        :return: The title of this DeployKey.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this DeployKey.


        :param title: The title of this DeployKey.  # noqa: E501
        :type title: str
        """

        self._title = title

    @property
    def url(self):
        """Gets the url of this DeployKey.  # noqa: E501


        :return: The url of this DeployKey.  # noqa: E501
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url):
        """Sets the url of this DeployKey.


        :param url: The url of this DeployKey.  # noqa: E501
        :type url: str
        """

        self._url = url

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
        if not isinstance(other, DeployKey):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DeployKey):
            return True

        return self.to_dict() != other.to_dict()
