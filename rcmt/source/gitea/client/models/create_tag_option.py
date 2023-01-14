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


class CreateTagOption(object):
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
        'message': 'str',
        'tag_name': 'str',
        'target': 'str'
    }

    attribute_map = {
        'message': 'message',
        'tag_name': 'tag_name',
        'target': 'target'
    }

    def __init__(self, message=None, tag_name=None, target=None, local_vars_configuration=None):  # noqa: E501
        """CreateTagOption - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._message = None
        self._tag_name = None
        self._target = None
        self.discriminator = None

        if message is not None:
            self.message = message
        self.tag_name = tag_name
        if target is not None:
            self.target = target

    @property
    def message(self):
        """Gets the message of this CreateTagOption.  # noqa: E501


        :return: The message of this CreateTagOption.  # noqa: E501
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this CreateTagOption.


        :param message: The message of this CreateTagOption.  # noqa: E501
        :type message: str
        """

        self._message = message

    @property
    def tag_name(self):
        """Gets the tag_name of this CreateTagOption.  # noqa: E501


        :return: The tag_name of this CreateTagOption.  # noqa: E501
        :rtype: str
        """
        return self._tag_name

    @tag_name.setter
    def tag_name(self, tag_name):
        """Sets the tag_name of this CreateTagOption.


        :param tag_name: The tag_name of this CreateTagOption.  # noqa: E501
        :type tag_name: str
        """
        if self.local_vars_configuration.client_side_validation and tag_name is None:  # noqa: E501
            raise ValueError("Invalid value for `tag_name`, must not be `None`")  # noqa: E501

        self._tag_name = tag_name

    @property
    def target(self):
        """Gets the target of this CreateTagOption.  # noqa: E501


        :return: The target of this CreateTagOption.  # noqa: E501
        :rtype: str
        """
        return self._target

    @target.setter
    def target(self, target):
        """Sets the target of this CreateTagOption.


        :param target: The target of this CreateTagOption.  # noqa: E501
        :type target: str
        """

        self._target = target

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
        if not isinstance(other, CreateTagOption):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateTagOption):
            return True

        return self.to_dict() != other.to_dict()
