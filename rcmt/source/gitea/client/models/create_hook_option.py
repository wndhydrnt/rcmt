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


class CreateHookOption(object):
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
        'active': 'bool',
        'branch_filter': 'str',
        'config': 'dict(str, str)',
        'events': 'list[str]',
        'type': 'str'
    }

    attribute_map = {
        'active': 'active',
        'branch_filter': 'branch_filter',
        'config': 'config',
        'events': 'events',
        'type': 'type'
    }

    def __init__(self, active=False, branch_filter=None, config=None, events=None, type=None, local_vars_configuration=None):  # noqa: E501
        """CreateHookOption - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._active = None
        self._branch_filter = None
        self._config = None
        self._events = None
        self._type = None
        self.discriminator = None

        if active is not None:
            self.active = active
        if branch_filter is not None:
            self.branch_filter = branch_filter
        self.config = config
        if events is not None:
            self.events = events
        self.type = type

    @property
    def active(self):
        """Gets the active of this CreateHookOption.  # noqa: E501


        :return: The active of this CreateHookOption.  # noqa: E501
        :rtype: bool
        """
        return self._active

    @active.setter
    def active(self, active):
        """Sets the active of this CreateHookOption.


        :param active: The active of this CreateHookOption.  # noqa: E501
        :type active: bool
        """

        self._active = active

    @property
    def branch_filter(self):
        """Gets the branch_filter of this CreateHookOption.  # noqa: E501


        :return: The branch_filter of this CreateHookOption.  # noqa: E501
        :rtype: str
        """
        return self._branch_filter

    @branch_filter.setter
    def branch_filter(self, branch_filter):
        """Sets the branch_filter of this CreateHookOption.


        :param branch_filter: The branch_filter of this CreateHookOption.  # noqa: E501
        :type branch_filter: str
        """

        self._branch_filter = branch_filter

    @property
    def config(self):
        """Gets the config of this CreateHookOption.  # noqa: E501

        CreateHookOptionConfig has all config options in it required are \"content_type\" and \"url\" Required  # noqa: E501

        :return: The config of this CreateHookOption.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._config

    @config.setter
    def config(self, config):
        """Sets the config of this CreateHookOption.

        CreateHookOptionConfig has all config options in it required are \"content_type\" and \"url\" Required  # noqa: E501

        :param config: The config of this CreateHookOption.  # noqa: E501
        :type config: dict(str, str)
        """
        if self.local_vars_configuration.client_side_validation and config is None:  # noqa: E501
            raise ValueError("Invalid value for `config`, must not be `None`")  # noqa: E501

        self._config = config

    @property
    def events(self):
        """Gets the events of this CreateHookOption.  # noqa: E501


        :return: The events of this CreateHookOption.  # noqa: E501
        :rtype: list[str]
        """
        return self._events

    @events.setter
    def events(self, events):
        """Sets the events of this CreateHookOption.


        :param events: The events of this CreateHookOption.  # noqa: E501
        :type events: list[str]
        """

        self._events = events

    @property
    def type(self):
        """Gets the type of this CreateHookOption.  # noqa: E501


        :return: The type of this CreateHookOption.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this CreateHookOption.


        :param type: The type of this CreateHookOption.  # noqa: E501
        :type type: str
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501
        allowed_values = ["dingtalk", "discord", "gitea", "gogs", "msteams", "slack", "telegram", "feishu", "wechatwork", "packagist"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and type not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"  # noqa: E501
                .format(type, allowed_values)
            )

        self._type = type

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
        if not isinstance(other, CreateHookOption):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateHookOption):
            return True

        return self.to_dict() != other.to_dict()
