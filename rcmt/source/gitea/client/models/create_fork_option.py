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


class CreateForkOption(object):
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
        'name': 'str',
        'organization': 'str'
    }

    attribute_map = {
        'name': 'name',
        'organization': 'organization'
    }

    def __init__(self, name=None, organization=None, local_vars_configuration=None):  # noqa: E501
        """CreateForkOption - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self._organization = None
        self.discriminator = None

        if name is not None:
            self.name = name
        if organization is not None:
            self.organization = organization

    @property
    def name(self):
        """Gets the name of this CreateForkOption.  # noqa: E501

        name of the forked repository  # noqa: E501

        :return: The name of this CreateForkOption.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this CreateForkOption.

        name of the forked repository  # noqa: E501

        :param name: The name of this CreateForkOption.  # noqa: E501
        :type name: str
        """

        self._name = name

    @property
    def organization(self):
        """Gets the organization of this CreateForkOption.  # noqa: E501

        organization name, if forking into an organization  # noqa: E501

        :return: The organization of this CreateForkOption.  # noqa: E501
        :rtype: str
        """
        return self._organization

    @organization.setter
    def organization(self, organization):
        """Sets the organization of this CreateForkOption.

        organization name, if forking into an organization  # noqa: E501

        :param organization: The organization of this CreateForkOption.  # noqa: E501
        :type organization: str
        """

        self._organization = organization

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
        if not isinstance(other, CreateForkOption):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateForkOption):
            return True

        return self.to_dict() != other.to_dict()
