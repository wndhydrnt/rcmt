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


class CreateMilestoneOption(object):
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
        'description': 'str',
        'due_on': 'datetime',
        'state': 'str',
        'title': 'str'
    }

    attribute_map = {
        'description': 'description',
        'due_on': 'due_on',
        'state': 'state',
        'title': 'title'
    }

    def __init__(self, description=None, due_on=None, state=None, title=None, local_vars_configuration=None):  # noqa: E501
        """CreateMilestoneOption - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._description = None
        self._due_on = None
        self._state = None
        self._title = None
        self.discriminator = None

        if description is not None:
            self.description = description
        if due_on is not None:
            self.due_on = due_on
        if state is not None:
            self.state = state
        if title is not None:
            self.title = title

    @property
    def description(self):
        """Gets the description of this CreateMilestoneOption.  # noqa: E501


        :return: The description of this CreateMilestoneOption.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CreateMilestoneOption.


        :param description: The description of this CreateMilestoneOption.  # noqa: E501
        :type description: str
        """

        self._description = description

    @property
    def due_on(self):
        """Gets the due_on of this CreateMilestoneOption.  # noqa: E501


        :return: The due_on of this CreateMilestoneOption.  # noqa: E501
        :rtype: datetime
        """
        return self._due_on

    @due_on.setter
    def due_on(self, due_on):
        """Sets the due_on of this CreateMilestoneOption.


        :param due_on: The due_on of this CreateMilestoneOption.  # noqa: E501
        :type due_on: datetime
        """

        self._due_on = due_on

    @property
    def state(self):
        """Gets the state of this CreateMilestoneOption.  # noqa: E501


        :return: The state of this CreateMilestoneOption.  # noqa: E501
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this CreateMilestoneOption.


        :param state: The state of this CreateMilestoneOption.  # noqa: E501
        :type state: str
        """
        allowed_values = ["open", "closed"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and state not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `state` ({0}), must be one of {1}"  # noqa: E501
                .format(state, allowed_values)
            )

        self._state = state

    @property
    def title(self):
        """Gets the title of this CreateMilestoneOption.  # noqa: E501


        :return: The title of this CreateMilestoneOption.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this CreateMilestoneOption.


        :param title: The title of this CreateMilestoneOption.  # noqa: E501
        :type title: str
        """

        self._title = title

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
        if not isinstance(other, CreateMilestoneOption):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateMilestoneOption):
            return True

        return self.to_dict() != other.to_dict()
