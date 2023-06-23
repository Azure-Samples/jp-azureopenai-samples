# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# coding: utf-8

"""
    Speech to Text API v3.0

    Speech to Text API v3.0.  # noqa: E501

    OpenAPI spec version: v3.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from swagger_client.configuration import Configuration


class ModelCopy(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'target_subscription_key': 'str'
    }

    attribute_map = {
        'target_subscription_key': 'targetSubscriptionKey'
    }

    def __init__(self, target_subscription_key=None, _configuration=None):  # noqa: E501
        """ModelCopy - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._target_subscription_key = None
        self.discriminator = None

        self.target_subscription_key = target_subscription_key

    @property
    def target_subscription_key(self):
        """Gets the target_subscription_key of this ModelCopy.  # noqa: E501

        The subscription key of the subscription that is the target of the copy operation.  # noqa: E501

        :return: The target_subscription_key of this ModelCopy.  # noqa: E501
        :rtype: str
        """
        return self._target_subscription_key

    @target_subscription_key.setter
    def target_subscription_key(self, target_subscription_key):
        """Sets the target_subscription_key of this ModelCopy.

        The subscription key of the subscription that is the target of the copy operation.  # noqa: E501

        :param target_subscription_key: The target_subscription_key of this ModelCopy.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and target_subscription_key is None:
            raise ValueError("Invalid value for `target_subscription_key`, must not be `None`")  # noqa: E501

        self._target_subscription_key = target_subscription_key

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(ModelCopy, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ModelCopy):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ModelCopy):
            return True

        return self.to_dict() != other.to_dict()
