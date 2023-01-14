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


class NodeInfoSoftware(object):
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
        'homepage': 'str',
        'name': 'str',
        'repository': 'str',
        'version': 'str'
    }

    attribute_map = {
        'homepage': 'homepage',
        'name': 'name',
        'repository': 'repository',
        'version': 'version'
    }

    def __init__(self, homepage=None, name=None, repository=None, version=None, local_vars_configuration=None):  # noqa: E501
        """NodeInfoSoftware - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._homepage = None
        self._name = None
        self._repository = None
        self._version = None
        self.discriminator = None

        if homepage is not None:
            self.homepage = homepage
        if name is not None:
            self.name = name
        if repository is not None:
            self.repository = repository
        if version is not None:
            self.version = version

    @property
    def homepage(self):
        """Gets the homepage of this NodeInfoSoftware.  # noqa: E501


        :return: The homepage of this NodeInfoSoftware.  # noqa: E501
        :rtype: str
        """
        return self._homepage

    @homepage.setter
    def homepage(self, homepage):
        """Sets the homepage of this NodeInfoSoftware.


        :param homepage: The homepage of this NodeInfoSoftware.  # noqa: E501
        :type homepage: str
        """

        self._homepage = homepage

    @property
    def name(self):
        """Gets the name of this NodeInfoSoftware.  # noqa: E501


        :return: The name of this NodeInfoSoftware.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this NodeInfoSoftware.


        :param name: The name of this NodeInfoSoftware.  # noqa: E501
        :type name: str
        """

        self._name = name

    @property
    def repository(self):
        """Gets the repository of this NodeInfoSoftware.  # noqa: E501


        :return: The repository of this NodeInfoSoftware.  # noqa: E501
        :rtype: str
        """
        return self._repository

    @repository.setter
    def repository(self, repository):
        """Sets the repository of this NodeInfoSoftware.


        :param repository: The repository of this NodeInfoSoftware.  # noqa: E501
        :type repository: str
        """

        self._repository = repository

    @property
    def version(self):
        """Gets the version of this NodeInfoSoftware.  # noqa: E501


        :return: The version of this NodeInfoSoftware.  # noqa: E501
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this NodeInfoSoftware.


        :param version: The version of this NodeInfoSoftware.  # noqa: E501
        :type version: str
        """

        self._version = version

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
        if not isinstance(other, NodeInfoSoftware):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, NodeInfoSoftware):
            return True

        return self.to_dict() != other.to_dict()
