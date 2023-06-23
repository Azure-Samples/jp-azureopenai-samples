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


class ManagementModelProperties(object):
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
        'purposes': 'list[str]',
        'model_class': 'str',
        'vad_kind': 'str',
        'uses_online_interpolation': 'bool',
        'cascade_delete': 'bool',
        'is_dynamic_grammar_supported': 'bool',
        'uses_halide': 'bool'
    }

    attribute_map = {
        'purposes': 'purposes',
        'model_class': 'modelClass',
        'vad_kind': 'vadKind',
        'uses_online_interpolation': 'usesOnlineInterpolation',
        'cascade_delete': 'cascadeDelete',
        'is_dynamic_grammar_supported': 'isDynamicGrammarSupported',
        'uses_halide': 'usesHalide'
    }

    def __init__(self, purposes=None, model_class=None, vad_kind=None, uses_online_interpolation=None, cascade_delete=None, is_dynamic_grammar_supported=None, uses_halide=None, _configuration=None):  # noqa: E501
        """ManagementModelProperties - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._purposes = None
        self._model_class = None
        self._vad_kind = None
        self._uses_online_interpolation = None
        self._cascade_delete = None
        self._is_dynamic_grammar_supported = None
        self._uses_halide = None
        self.discriminator = None

        if purposes is not None:
            self.purposes = purposes
        if model_class is not None:
            self.model_class = model_class
        if vad_kind is not None:
            self.vad_kind = vad_kind
        if uses_online_interpolation is not None:
            self.uses_online_interpolation = uses_online_interpolation
        if cascade_delete is not None:
            self.cascade_delete = cascade_delete
        if is_dynamic_grammar_supported is not None:
            self.is_dynamic_grammar_supported = is_dynamic_grammar_supported
        if uses_halide is not None:
            self.uses_halide = uses_halide

    @property
    def purposes(self):
        """Gets the purposes of this ManagementModelProperties.  # noqa: E501


        :return: The purposes of this ManagementModelProperties.  # noqa: E501
        :rtype: list[str]
        """
        return self._purposes

    @purposes.setter
    def purposes(self, purposes):
        """Sets the purposes of this ManagementModelProperties.


        :param purposes: The purposes of this ManagementModelProperties.  # noqa: E501
        :type: list[str]
        """
        allowed_values = ["BatchTranscription", "OnlineTranscription", "LanguageAdaptation", "AcousticAdaptation", "LanguageOnlineInterpolation"]  # noqa: E501
        if (self._configuration.client_side_validation and
                not set(purposes).issubset(set(allowed_values))):  # noqa: E501
            raise ValueError(
                "Invalid values for `purposes` [{0}], must be a subset of [{1}]"  # noqa: E501
                .format(", ".join(map(str, set(purposes) - set(allowed_values))),  # noqa: E501
                        ", ".join(map(str, allowed_values)))
            )

        self._purposes = purposes

    @property
    def model_class(self):
        """Gets the model_class of this ManagementModelProperties.  # noqa: E501


        :return: The model_class of this ManagementModelProperties.  # noqa: E501
        :rtype: str
        """
        return self._model_class

    @model_class.setter
    def model_class(self, model_class):
        """Sets the model_class of this ManagementModelProperties.


        :param model_class: The model_class of this ManagementModelProperties.  # noqa: E501
        :type: str
        """
        allowed_values = ["None", "Unifiedv2", "Unifiedv4", "Unifiedv4Pch"]  # noqa: E501
        if (self._configuration.client_side_validation and
                model_class not in allowed_values):
            raise ValueError(
                "Invalid value for `model_class` ({0}), must be one of {1}"  # noqa: E501
                .format(model_class, allowed_values)
            )

        self._model_class = model_class

    @property
    def vad_kind(self):
        """Gets the vad_kind of this ManagementModelProperties.  # noqa: E501


        :return: The vad_kind of this ManagementModelProperties.  # noqa: E501
        :rtype: str
        """
        return self._vad_kind

    @vad_kind.setter
    def vad_kind(self, vad_kind):
        """Sets the vad_kind of this ManagementModelProperties.


        :param vad_kind: The vad_kind of this ManagementModelProperties.  # noqa: E501
        :type: str
        """
        allowed_values = ["None", "Tuned"]  # noqa: E501
        if (self._configuration.client_side_validation and
                vad_kind not in allowed_values):
            raise ValueError(
                "Invalid value for `vad_kind` ({0}), must be one of {1}"  # noqa: E501
                .format(vad_kind, allowed_values)
            )

        self._vad_kind = vad_kind

    @property
    def uses_online_interpolation(self):
        """Gets the uses_online_interpolation of this ManagementModelProperties.  # noqa: E501


        :return: The uses_online_interpolation of this ManagementModelProperties.  # noqa: E501
        :rtype: bool
        """
        return self._uses_online_interpolation

    @uses_online_interpolation.setter
    def uses_online_interpolation(self, uses_online_interpolation):
        """Sets the uses_online_interpolation of this ManagementModelProperties.


        :param uses_online_interpolation: The uses_online_interpolation of this ManagementModelProperties.  # noqa: E501
        :type: bool
        """

        self._uses_online_interpolation = uses_online_interpolation

    @property
    def cascade_delete(self):
        """Gets the cascade_delete of this ManagementModelProperties.  # noqa: E501


        :return: The cascade_delete of this ManagementModelProperties.  # noqa: E501
        :rtype: bool
        """
        return self._cascade_delete

    @cascade_delete.setter
    def cascade_delete(self, cascade_delete):
        """Sets the cascade_delete of this ManagementModelProperties.


        :param cascade_delete: The cascade_delete of this ManagementModelProperties.  # noqa: E501
        :type: bool
        """

        self._cascade_delete = cascade_delete

    @property
    def is_dynamic_grammar_supported(self):
        """Gets the is_dynamic_grammar_supported of this ManagementModelProperties.  # noqa: E501


        :return: The is_dynamic_grammar_supported of this ManagementModelProperties.  # noqa: E501
        :rtype: bool
        """
        return self._is_dynamic_grammar_supported

    @is_dynamic_grammar_supported.setter
    def is_dynamic_grammar_supported(self, is_dynamic_grammar_supported):
        """Sets the is_dynamic_grammar_supported of this ManagementModelProperties.


        :param is_dynamic_grammar_supported: The is_dynamic_grammar_supported of this ManagementModelProperties.  # noqa: E501
        :type: bool
        """

        self._is_dynamic_grammar_supported = is_dynamic_grammar_supported

    @property
    def uses_halide(self):
        """Gets the uses_halide of this ManagementModelProperties.  # noqa: E501


        :return: The uses_halide of this ManagementModelProperties.  # noqa: E501
        :rtype: bool
        """
        return self._uses_halide

    @uses_halide.setter
    def uses_halide(self, uses_halide):
        """Sets the uses_halide of this ManagementModelProperties.


        :param uses_halide: The uses_halide of this ManagementModelProperties.  # noqa: E501
        :type: bool
        """

        self._uses_halide = uses_halide

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
        if issubclass(ManagementModelProperties, dict):
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
        if not isinstance(other, ManagementModelProperties):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ManagementModelProperties):
            return True

        return self.to_dict() != other.to_dict()
