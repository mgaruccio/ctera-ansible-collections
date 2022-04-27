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
module: ctera_portal_plan
short_description: CTERA-Networks Portal Plan configuration and management
description:
    - Create, modify and delete plans.
extends_documentation_fragment:
    - ctera.ctera.vportal

author:
    - Saimon Michelson (@saimonation)
    - Ygal Blum (@ygalblum)

options:
  state:
    description:
    - Whether the specified plan should exist or not.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  name:
    description: The name of the plan
    required: True
    type: str
  retention:
    description: The data retention policy
    type: list
    elements: dict
    suboptions:
      policy_name:
        description: The name of the policy
        type: str
        required: True
        choices:
          - retainAll
          - hourly
          - daily
          - weekly
          - monthly
          - quarterly
          - yearly
          - retainDeleted
      duration:
        description: The duration for the policy
        type: int
        required: True
  quotas:
    description: The items included in the plan and their respective quota
    type: list
    elements: dict
    suboptions:
      item_name:
        description: The name of the plan item
        type: str
        required: True
        choices:
        - EV4
        - EV8
        - EV16
        - EV32
        - EV64
        - EV128
        - WA
        - SA
        - Share
        - Connect
        - Storage
      amount:
        description: The quota's amount
        type: int
        required: True

'''

EXAMPLES = '''
- name: Portal Plan
  ctera_portal_plan:
    name: 'example'
    retention:
    - policy_name: retainAll
      duration: 24
    quotas:
    - item_name: EV16
      amount: 100
    ctera_host: "{{ ctera_portal_hostname }}"
    ctera_user: "{{ ctera_portal_user }}"
    ctera_password: "{{ ctera_portal_password }}"
'''

RETURN = '''
name:
  description: Name of the Plan
  returned: when state is present
  type: str
  sample: example
'''
from ansible_collections.ctera.ctera.plugins.module_utils import ctera_common
from ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base import CteraPortalBase

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraPortalPlan(CteraPortalBase):
    _create_params = ['name', 'email', 'first_name', 'last_name', 'password', 'role', 'company', 'comment', 'password_change']
    _retention_policy_names = ['retainAll', 'hourly', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'retainDeleted']
    _quotas_item_names = ['EV4', 'EV8', 'EV16', 'EV32', 'EV64', 'EV128', 'WA', 'SA', 'Share', 'Connect', 'Storage']

    def __init__(self):
        super().__init__(
            dict(
                state=dict(required=False, choices=['present', 'absent'], default='present'),
                name=dict(type='str', required=True),
                retention=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        policy_name=dict(type='str', required=True, choices=CteraPortalPlan._retention_policy_names),
                        duration=dict(type='int', required=True)
                    )
                ),
                quotas=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        item_name=dict(type='str', required=True, choices=CteraPortalPlan._quotas_item_names),
                        amount=dict(type='int', required=True)
                    )
                )
            )
        )

    @property
    def _generic_failure_message(self):  # pragma: no cover
        return 'Plan management failed'

    def _execute(self):
        state = self.parameters.pop('state')
        plan = self._get_plan()
        if state == 'present':
            self._ensure_present(plan)
        else:
            self._ensure_absent(plan)

    def _get_plan(self):
        plan = None
        try:
            plan = self._ctera_portal.plans.get(
                self.parameters['name'],
                include=[
                    'name',
                    'retentionPolicy',
                    'vGateways4',
                    'vGateways8',
                    'appliances',
                    'vGateways32',
                    'vGateways64',
                    'vGateways128',
                    'workstationAgents',
                    'serverAgents',
                    'cloudDrives',
                    'cloudDrivesLite',
                    'storage',
                ]
            )
        except CTERAException:
            pass
        return self._to_plan_dict(plan) if plan else None

    def _ensure_present(self, plan):
        if plan:
            modified_attributes = ctera_common.get_modified_attributes(plan, self.parameters)
            if modified_attributes:
                self._ctera_portal.plans.modify(self.parameters['name'], **self._translate_params_obj(modified_attributes))
                self.ansible_module.ctera_return_value().changed().msg('Plan modified').put(name=self.parameters['name'])
            else:
                self.ansible_module.ctera_return_value().skipped().msg('Plan details did not change').put(name=self.parameters['name'])
        else:
            self._ctera_portal.plans.add(self.parameters['name'], **self._translate_params_obj(self.parameters))
            self.ansible_module.ctera_return_value().changed().msg('Plan created').put(name=self.parameters['name'])

    @staticmethod
    def _translate_params_obj(parameters):
        return dict(
            retention={i['policy_name']: i['duration'] for i in parameters['retention']} if parameters.get('retention') else None,
            quotas={i['item_name']: i['amount'] for i in parameters['quotas']} if parameters.get('quotas') else None
        )

    def _ensure_absent(self, plan):
        if plan:
            self._ctera_portal.plans.delete(self.parameters['name'])
            self.ansible_module.ctera_return_value().changed().msg('Plan deleted').put(name=self.parameters['name'])
        else:
            self.ansible_module.ctera_return_value().skipped().msg('Plan already does not exist').put(name=self.parameters['name'])

    @staticmethod
    def _to_plan_dict(plan):
        return dict(
            name=plan.name,
            retention=[
                dict(policy_name=k, duration=v) for k, v in plan.retentionPolicy.__dict__.items() if not k.startswith("_")
            ],
            quotas=[
                dict(item_name='EV4', amount=plan.vGateways4.amount),
                dict(item_name='EV8', amount=plan.vGateways8.amount),
                dict(item_name='EV16', amount=plan.appliances.amount),
                dict(item_name='EV64', amount=plan.vGateways64.amount),
                dict(item_name='EV128', amount=plan.vGateways128.amount),
                dict(item_name='WA', amount=plan.workstationAgents.amount),
                dict(item_name='SA', amount=plan.serverAgents.amount),
                dict(item_name='Share', amount=plan.cloudDrives.amount),
                dict(item_name='Connect', amount=plan.cloudDrivesLite.amount),
                dict(item_name='Storage', amount=plan.storage.amount),
            ]
        )


def main():  # pragma: no cover
    CteraPortalPlan().run()


if __name__ == '__main__':  # pragma: no cover
    main()
