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
module: ctera_portal_folder_group
short_description: CTERA-Networks Portal folder group configuration and management
description:
    - Create, and delete folder groups.
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether the specified user should exist or not.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  name:
    description: The name of the folder group
    required: True
    type: str
  owner:
    description: The folder group owner
    type: dict
    suboptions:
      name:
        description: The user name
        required: True
        type: str
      directory:
        description: The fully-qualified name of the user directory, if the user belongs to one
        type: str

'''

EXAMPLES = '''
- name: No Owner Folder Group
  ctera_portal_folder_group:
    name: 'CompanyMain'
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"

- name: User Owned Folder Group
  ctera_portal_folder_group:
    name: "CompanyMain"
    owner:
      name: "Alice"
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"

'''

RETURN = '''
name:
  description: Name of the folder group
  returned: when state is present
  type: str
  sample: CompanyMain
'''

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base import CteraPortalBase

try:
    from cterasdk import CTERAException, portal_types
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraPortalFolderGroup(CteraPortalBase):
    def __init__(self):
        super().__init__(
            dict(
                state=dict(required=False, choices=['present', 'absent'], default='present'),
                name=dict(type='str', required=True),
                owner=dict(
                    type='dict',
                    required=False,
                    options=dict(
                        name=dict(type='str', required=True),
                        directory=dict(type='str')
                    )
                ),
            )
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Folder Group management failed'

    def _execute(self):
        state = self.parameters.pop('state')
        folder_group = self._get_folder_group()
        if state == 'present':
            self._ensure_present(folder_group)
        else:
            self._ensure_absent(folder_group)

    def _get_folder_group(self):
        folder_group = []
        try:
            folder_group = self._ctera_portal.cloudfs.get(self.parameters['name'])
        except CTERAException:
            pass
        return self._to_folder_group_dict(folder_group) if folder_group else None

    @staticmethod
    def _make_user_account(user_details):
        return portal_types.UserAccount(**user_details) if user_details else None

    @staticmethod
    def _to_folder_group_dict(folder_group):
        return dict(
            name=folder_group.name,
            owner=dict(name=folder_group.owner.split('/')[-1]) if folder_group.owner else None
        )

    def _ensure_present(self, folder_group):
        if folder_group:
            self.ansible_module.ctera_return_value().skipped().msg('Folder Group already exists').put(name=self.parameters['name'])
        else:
            self._ctera_portal.cloudfs.mkfg(self.parameters['name'], user=self._make_user_account(self.parameters.get('owner')))
            self.ansible_module.ctera_return_value().changed().msg('Folder Group created').put(name=self.parameters['name'])

    def _ensure_absent(self, folder_group):
        if folder_group:
            self._ctera_portal.cloudfs.rmfg(self.parameters['name'])
            self.ansible_module.ctera_return_value().changed().msg('Folder Group deleted').put(name=self.parameters['name'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Folder Group already does not exist').put(name=self.parameters['name'])


def main():  # pragma: no cover
    CteraPortalFolderGroup().run()


if __name__ == '__main__':  # pragma: no cover
    main()
