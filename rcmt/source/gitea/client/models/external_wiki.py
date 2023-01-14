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


class ExternalWiki(object):
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
        'external_wiki_url': 'str'
    }

    attribute_map = {
        'external_wiki_url': 'external_wiki_url'
    }

    def __init__(self, external_wiki_url=None, local_vars_configuration=None):  # noqa: E501
        """ExternalWiki - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._external_wiki_url = None
        self.discriminator = None

        if external_wiki_url is not None:
            self.external_wiki_url = external_wiki_url

    @property
    def external_wiki_url(self):
        """Gets the external_wiki_url of this ExternalWiki.  # noqa: E501

        URL of external wiki.  # noqa: E501

        :return: The external_wiki_url of this ExternalWiki.  # noqa: E501
        :rtype: str
        """
        return self._external_wiki_url

    @external_wiki_url.setter
    def external_wiki_url(self, external_wiki_url):
        """Sets the external_wiki_url of this ExternalWiki.

        URL of external wiki.  # noqa: E501

        :param external_wiki_url: The external_wiki_url of this ExternalWiki.  # noqa: E501
        :type external_wiki_url: str
        """

        self._external_wiki_url = external_wiki_url

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
        if not isinstance(other, ExternalWiki):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ExternalWiki):
            return True

        return self.to_dict() != other.to_dict()