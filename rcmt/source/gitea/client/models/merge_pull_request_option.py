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


class MergePullRequestOption(object):
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
        'do': 'str',
        'merge_commit_id': 'str',
        'merge_message_field': 'str',
        'merge_title_field': 'str',
        'delete_branch_after_merge': 'bool',
        'force_merge': 'bool',
        'head_commit_id': 'str',
        'merge_when_checks_succeed': 'bool'
    }

    attribute_map = {
        'do': 'Do',
        'merge_commit_id': 'MergeCommitID',
        'merge_message_field': 'MergeMessageField',
        'merge_title_field': 'MergeTitleField',
        'delete_branch_after_merge': 'delete_branch_after_merge',
        'force_merge': 'force_merge',
        'head_commit_id': 'head_commit_id',
        'merge_when_checks_succeed': 'merge_when_checks_succeed'
    }

    def __init__(self, do=None, merge_commit_id=None, merge_message_field=None, merge_title_field=None, delete_branch_after_merge=None, force_merge=None, head_commit_id=None, merge_when_checks_succeed=None, local_vars_configuration=None):  # noqa: E501
        """MergePullRequestOption - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._do = None
        self._merge_commit_id = None
        self._merge_message_field = None
        self._merge_title_field = None
        self._delete_branch_after_merge = None
        self._force_merge = None
        self._head_commit_id = None
        self._merge_when_checks_succeed = None
        self.discriminator = None

        self.do = do
        if merge_commit_id is not None:
            self.merge_commit_id = merge_commit_id
        if merge_message_field is not None:
            self.merge_message_field = merge_message_field
        if merge_title_field is not None:
            self.merge_title_field = merge_title_field
        if delete_branch_after_merge is not None:
            self.delete_branch_after_merge = delete_branch_after_merge
        if force_merge is not None:
            self.force_merge = force_merge
        if head_commit_id is not None:
            self.head_commit_id = head_commit_id
        if merge_when_checks_succeed is not None:
            self.merge_when_checks_succeed = merge_when_checks_succeed

    @property
    def do(self):
        """Gets the do of this MergePullRequestOption.  # noqa: E501


        :return: The do of this MergePullRequestOption.  # noqa: E501
        :rtype: str
        """
        return self._do

    @do.setter
    def do(self, do):
        """Sets the do of this MergePullRequestOption.


        :param do: The do of this MergePullRequestOption.  # noqa: E501
        :type do: str
        """
        if self.local_vars_configuration.client_side_validation and do is None:  # noqa: E501
            raise ValueError("Invalid value for `do`, must not be `None`")  # noqa: E501
        allowed_values = ["merge", "rebase", "rebase-merge", "squash", "manually-merged"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and do not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `do` ({0}), must be one of {1}"  # noqa: E501
                .format(do, allowed_values)
            )

        self._do = do

    @property
    def merge_commit_id(self):
        """Gets the merge_commit_id of this MergePullRequestOption.  # noqa: E501


        :return: The merge_commit_id of this MergePullRequestOption.  # noqa: E501
        :rtype: str
        """
        return self._merge_commit_id

    @merge_commit_id.setter
    def merge_commit_id(self, merge_commit_id):
        """Sets the merge_commit_id of this MergePullRequestOption.


        :param merge_commit_id: The merge_commit_id of this MergePullRequestOption.  # noqa: E501
        :type merge_commit_id: str
        """

        self._merge_commit_id = merge_commit_id

    @property
    def merge_message_field(self):
        """Gets the merge_message_field of this MergePullRequestOption.  # noqa: E501


        :return: The merge_message_field of this MergePullRequestOption.  # noqa: E501
        :rtype: str
        """
        return self._merge_message_field

    @merge_message_field.setter
    def merge_message_field(self, merge_message_field):
        """Sets the merge_message_field of this MergePullRequestOption.


        :param merge_message_field: The merge_message_field of this MergePullRequestOption.  # noqa: E501
        :type merge_message_field: str
        """

        self._merge_message_field = merge_message_field

    @property
    def merge_title_field(self):
        """Gets the merge_title_field of this MergePullRequestOption.  # noqa: E501


        :return: The merge_title_field of this MergePullRequestOption.  # noqa: E501
        :rtype: str
        """
        return self._merge_title_field

    @merge_title_field.setter
    def merge_title_field(self, merge_title_field):
        """Sets the merge_title_field of this MergePullRequestOption.


        :param merge_title_field: The merge_title_field of this MergePullRequestOption.  # noqa: E501
        :type merge_title_field: str
        """

        self._merge_title_field = merge_title_field

    @property
    def delete_branch_after_merge(self):
        """Gets the delete_branch_after_merge of this MergePullRequestOption.  # noqa: E501


        :return: The delete_branch_after_merge of this MergePullRequestOption.  # noqa: E501
        :rtype: bool
        """
        return self._delete_branch_after_merge

    @delete_branch_after_merge.setter
    def delete_branch_after_merge(self, delete_branch_after_merge):
        """Sets the delete_branch_after_merge of this MergePullRequestOption.


        :param delete_branch_after_merge: The delete_branch_after_merge of this MergePullRequestOption.  # noqa: E501
        :type delete_branch_after_merge: bool
        """

        self._delete_branch_after_merge = delete_branch_after_merge

    @property
    def force_merge(self):
        """Gets the force_merge of this MergePullRequestOption.  # noqa: E501


        :return: The force_merge of this MergePullRequestOption.  # noqa: E501
        :rtype: bool
        """
        return self._force_merge

    @force_merge.setter
    def force_merge(self, force_merge):
        """Sets the force_merge of this MergePullRequestOption.


        :param force_merge: The force_merge of this MergePullRequestOption.  # noqa: E501
        :type force_merge: bool
        """

        self._force_merge = force_merge

    @property
    def head_commit_id(self):
        """Gets the head_commit_id of this MergePullRequestOption.  # noqa: E501


        :return: The head_commit_id of this MergePullRequestOption.  # noqa: E501
        :rtype: str
        """
        return self._head_commit_id

    @head_commit_id.setter
    def head_commit_id(self, head_commit_id):
        """Sets the head_commit_id of this MergePullRequestOption.


        :param head_commit_id: The head_commit_id of this MergePullRequestOption.  # noqa: E501
        :type head_commit_id: str
        """

        self._head_commit_id = head_commit_id

    @property
    def merge_when_checks_succeed(self):
        """Gets the merge_when_checks_succeed of this MergePullRequestOption.  # noqa: E501


        :return: The merge_when_checks_succeed of this MergePullRequestOption.  # noqa: E501
        :rtype: bool
        """
        return self._merge_when_checks_succeed

    @merge_when_checks_succeed.setter
    def merge_when_checks_succeed(self, merge_when_checks_succeed):
        """Sets the merge_when_checks_succeed of this MergePullRequestOption.


        :param merge_when_checks_succeed: The merge_when_checks_succeed of this MergePullRequestOption.  # noqa: E501
        :type merge_when_checks_succeed: bool
        """

        self._merge_when_checks_succeed = merge_when_checks_succeed

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
        if not isinstance(other, MergePullRequestOption):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MergePullRequestOption):
            return True

        return self.to_dict() != other.to_dict()
