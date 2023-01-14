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


class PullRequestMeta(object):
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
        'merged': 'bool',
        'merged_at': 'datetime'
    }

    attribute_map = {
        'merged': 'merged',
        'merged_at': 'merged_at'
    }

    def __init__(self, merged=None, merged_at=None, local_vars_configuration=None):  # noqa: E501
        """PullRequestMeta - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._merged = None
        self._merged_at = None
        self.discriminator = None

        if merged is not None:
            self.merged = merged
        if merged_at is not None:
            self.merged_at = merged_at

    @property
    def merged(self):
        """Gets the merged of this PullRequestMeta.  # noqa: E501


        :return: The merged of this PullRequestMeta.  # noqa: E501
        :rtype: bool
        """
        return self._merged

    @merged.setter
    def merged(self, merged):
        """Sets the merged of this PullRequestMeta.


        :param merged: The merged of this PullRequestMeta.  # noqa: E501
        :type merged: bool
        """

        self._merged = merged

    @property
    def merged_at(self):
        """Gets the merged_at of this PullRequestMeta.  # noqa: E501


        :return: The merged_at of this PullRequestMeta.  # noqa: E501
        :rtype: datetime
        """
        return self._merged_at

    @merged_at.setter
    def merged_at(self, merged_at):
        """Sets the merged_at of this PullRequestMeta.


        :param merged_at: The merged_at of this PullRequestMeta.  # noqa: E501
        :type merged_at: datetime
        """

        self._merged_at = merged_at

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
        if not isinstance(other, PullRequestMeta):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PullRequestMeta):
            return True

        return self.to_dict() != other.to_dict()
