#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, CTERA Networks Ltd.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ctera_filer_array
short_description: CTERA-Networks Filer array configuration and management
description:
    - Create, modify and delete arrays.
version_added: "2.10"
extends_documentation_fragment:
    - ctera.ctera.filer

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether the specified volume should exist or not.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  name:
    description: The name of the array
    required: True
    type: str
  level:
    description: RAID level to use, Required if C(state=present)
    type: str
    choices:
      - linear
      - 0
      - 1
      - 5
      - 6
  members:
    description: Members of the array, if empty, assign all unassigned drives
    type: list
    elements: str

requirements:
    - cterasdk
'''

EXAMPLES = '''
- name: create new array
  ctera_filer_array:
    name: main
    level: linear
    members:
      - SATA1-0-1
    filer_host: "{{ ctera_filer_hostname }}"
    filer_user: "{{ ctera_filer_user }}"
    filer_password: "{{ ctera_filer_password }}"
'''

RETURN = '''
name:
  description: Name of the newly created array
  returned: when state is present
  type: str
  sample: main
'''

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_common as ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_filer_base import CteraFilerBase

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraFilerArray(CteraFilerBase):
    _create_params = ['name', 'level', 'members']

    def __init__(self):
        super().__init__(
            dict(
                state=dict(required=False, choices=['present', 'absent'], default='present'),
                name=dict(type='str', required=True),
                level=dict(type='str', required=False, choices=['linear', '0', '1', '5', '6']),
                members=dict(type='list', required=False, elements='str')
            ),
            required_if=[('state', 'present', ['level'])]
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Array management failed'

    def _execute(self):
        state = self.parameters.pop('state')
        array = self._get_array()
        if state == 'present':
            self._ensure_present(array)
        else:
            self._ensure_absent(array)

    def _ensure_present(self, array):
        self._update_requested_members()
        if array:
            modified_attributes = ctera_common.get_modified_attributes(array, self.parameters)
            if modified_attributes:
                self.ansible_module.ctera_return_value().skipped().msg('Currently modifying arrays is not supported').put(name=self.parameters['name'])
            else:
                self.ansible_module.ctera_return_value().skipped().msg('Array details did not change').put(name=self.parameters['name'])
        else:
            create_params = {k: v for k, v in self.parameters.items() if k in CteraFilerArray._create_params}
            self._ctera_filer.array.add(**create_params)
            self.ansible_module.ctera_return_value().changed().msg('Array created').put(**create_params)

    def _ensure_absent(self, array):
        if array:
            self._ctera_filer.array.delete(self.parameters['name'])
            self.ansible_module.ctera_return_value().changed().msg('Volume deleted').put(name=self.parameters['name'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Array already does not exist').put(name=self.parameters['name'])

    def _get_array(self):
        array = None
        try:
            array = self._ctera_filer.array.get(name=self.parameters['name'])
        except CTERAException as error:
            if error.response.code != 404:  # pylint: disable=no-member
                raise
        return self._to_array_dict(array) if array else {}

    @staticmethod
    def _to_array_dict(array):
        array_dict = {k: v for k, v in array.__dict__.items() if not k.startswith("_")}
        return array_dict

    def _update_requested_members(self):
        self.parameters['members'] = self.parameters['members'] or \
            [d.name for d in self._ctera_filer.drive.get() if d.assignment == 'unassigned']


def main():  # pragma: no cover
    CteraFilerArray().run()


if __name__ == '__main__':  # pragma: no cover
    main()
