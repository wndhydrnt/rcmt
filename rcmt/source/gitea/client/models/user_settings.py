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


class UserSettings(object):
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
        'diff_view_style': 'str',
        'full_name': 'str',
        'hide_activity': 'bool',
        'hide_email': 'bool',
        'language': 'str',
        'location': 'str',
        'theme': 'str',
        'website': 'str'
    }

    attribute_map = {
        'description': 'description',
        'diff_view_style': 'diff_view_style',
        'full_name': 'full_name',
        'hide_activity': 'hide_activity',
        'hide_email': 'hide_email',
        'language': 'language',
        'location': 'location',
        'theme': 'theme',
        'website': 'website'
    }

    def __init__(self, description=None, diff_view_style=None, full_name=None, hide_activity=None, hide_email=None, language=None, location=None, theme=None, website=None, local_vars_configuration=None):  # noqa: E501
        """UserSettings - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._description = None
        self._diff_view_style = None
        self._full_name = None
        self._hide_activity = None
        self._hide_email = None
        self._language = None
        self._location = None
        self._theme = None
        self._website = None
        self.discriminator = None

        if description is not None:
            self.description = description
        if diff_view_style is not None:
            self.diff_view_style = diff_view_style
        if full_name is not None:
            self.full_name = full_name
        if hide_activity is not None:
            self.hide_activity = hide_activity
        if hide_email is not None:
            self.hide_email = hide_email
        if language is not None:
            self.language = language
        if location is not None:
            self.location = location
        if theme is not None:
            self.theme = theme
        if website is not None:
            self.website = website

    @property
    def description(self):
        """Gets the description of this UserSettings.  # noqa: E501


        :return: The description of this UserSettings.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this UserSettings.


        :param description: The description of this UserSettings.  # noqa: E501
        :type description: str
        """

        self._description = description

    @property
    def diff_view_style(self):
        """Gets the diff_view_style of this UserSettings.  # noqa: E501


        :return: The diff_view_style of this UserSettings.  # noqa: E501
        :rtype: str
        """
        return self._diff_view_style

    @diff_view_style.setter
    def diff_view_style(self, diff_view_style):
        """Sets the diff_view_style of this UserSettings.


        :param diff_view_style: The diff_view_style of this UserSettings.  # noqa: E501
        :type diff_view_style: str
        """

        self._diff_view_style = diff_view_style

    @property
    def full_name(self):
        """Gets the full_name of this UserSettings.  # noqa: E501


        :return: The full_name of this UserSettings.  # noqa: E501
        :rtype: str
        """
        return self._full_name

    @full_name.setter
    def full_name(self, full_name):
        """Sets the full_name of this UserSettings.


        :param full_name: The full_name of this UserSettings.  # noqa: E501
        :type full_name: str
        """

        self._full_name = full_name

    @property
    def hide_activity(self):
        """Gets the hide_activity of this UserSettings.  # noqa: E501


        :return: The hide_activity of this UserSettings.  # noqa: E501
        :rtype: bool
        """
        return self._hide_activity

    @hide_activity.setter
    def hide_activity(self, hide_activity):
        """Sets the hide_activity of this UserSettings.


        :param hide_activity: The hide_activity of this UserSettings.  # noqa: E501
        :type hide_activity: bool
        """

        self._hide_activity = hide_activity

    @property
    def hide_email(self):
        """Gets the hide_email of this UserSettings.  # noqa: E501

        Privacy  # noqa: E501

        :return: The hide_email of this UserSettings.  # noqa: E501
        :rtype: bool
        """
        return self._hide_email

    @hide_email.setter
    def hide_email(self, hide_email):
        """Sets the hide_email of this UserSettings.

        Privacy  # noqa: E501

        :param hide_email: The hide_email of this UserSettings.  # noqa: E501
        :type hide_email: bool
        """

        self._hide_email = hide_email

    @property
    def language(self):
        """Gets the language of this UserSettings.  # noqa: E501


        :return: The language of this UserSettings.  # noqa: E501
        :rtype: str
        """
        return self._language

    @language.setter
    def language(self, language):
        """Sets the language of this UserSettings.


        :param language: The language of this UserSettings.  # noqa: E501
        :type language: str
        """

        self._language = language

    @property
    def location(self):
        """Gets the location of this UserSettings.  # noqa: E501


        :return: The location of this UserSettings.  # noqa: E501
        :rtype: str
        """
        return self._location

    @location.setter
    def location(self, location):
        """Sets the location of this UserSettings.


        :param location: The location of this UserSettings.  # noqa: E501
        :type location: str
        """

        self._location = location

    @property
    def theme(self):
        """Gets the theme of this UserSettings.  # noqa: E501


        :return: The theme of this UserSettings.  # noqa: E501
        :rtype: str
        """
        return self._theme

    @theme.setter
    def theme(self, theme):
        """Sets the theme of this UserSettings.


        :param theme: The theme of this UserSettings.  # noqa: E501
        :type theme: str
        """

        self._theme = theme

    @property
    def website(self):
        """Gets the website of this UserSettings.  # noqa: E501


        :return: The website of this UserSettings.  # noqa: E501
        :rtype: str
        """
        return self._website

    @website.setter
    def website(self, website):
        """Sets the website of this UserSettings.


        :param website: The website of this UserSettings.  # noqa: E501
        :type website: str
        """

        self._website = website

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
        if not isinstance(other, UserSettings):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UserSettings):
            return True

        return self.to_dict() != other.to_dict()
