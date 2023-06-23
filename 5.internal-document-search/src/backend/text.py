# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

def nonewlines(s: str) -> str:
    return s.replace('\n', ' ').replace('\r', ' ')

