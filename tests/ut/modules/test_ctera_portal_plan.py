# pylint: disable=protected-access

# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is licensed under the Apache License 2.0.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright 2020, CTERA Networks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import copy
import unittest.mock as mock
import munch

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

from ansible_collections.ctera.ctera.plugins.modules.ctera_portal_plan import CteraPortalPlan
import tests.ut.mocks.ctera_portal_base_mock as ctera_portal_base_mock
from tests.ut.base import BaseTest


class TestCteraPortalPlan(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_portal_base_mock.mock_bases(self, CteraPortalPlan)

    def test__execute(self):
        for is_present in [True, False]:
            self._test__execute(is_present)

    @staticmethod
    def _test__execute(is_present):
        plan = CteraPortalPlan()
        plan.parameters = dict(state='present' if is_present else 'absent')
        plan._get_plan = mock.MagicMock(return_value=dict())
        plan._ensure_present = mock.MagicMock()
        plan._ensure_absent = mock.MagicMock()
        plan._execute()
        if is_present:
            plan._ensure_present.assert_called_once_with(mock.ANY)
            plan._ensure_absent.assert_not_called()
        else:
            plan._ensure_absent.assert_called_once_with(mock.ANY)
            plan._ensure_present.assert_not_called()

    def test_get_user_exists(self):
        expected_user_dict = dict(
            name='main',
            retention=[
                dict(policy_name='retainAll', duration=11),
                dict(policy_name='hourly', duration=12),
                dict(policy_name='daily', duration=13),
                dict(policy_name='weekly', duration=14),
                dict(policy_name='monthly', duration=15),
                dict(policy_name='quarterly', duration=16),
                dict(policy_name='yearly', duration=17),
                dict(policy_name='retainDeleted', duration=18)
            ],
            quotas=[
                dict(item_name='EV4', amount=21),
                dict(item_name='EV8', amount=22),
                dict(item_name='EV16', amount=23),
                dict(item_name='EV64', amount=24),
                dict(item_name='EV128', amount=25),
                dict(item_name='WA', amount=26),
                dict(item_name='SA', amount=27),
                dict(item_name='Share', amount=28),
                dict(item_name='Connect', amount=29)
            ]
        )
        returned_dict = munch.Munch(dict(
            name='main',
            retentionPolicy=munch.Munch(dict(
                retainAll=11,
                hourly=12,
                daily=13,
                weekly=14,
                monthly=15,
                quarterly=16,
                yearly=17,
                retainDeleted=18
            )),
            vGateways4=munch.Munch(dict(amount=21)),
            vGateways8=munch.Munch(dict(amount=22)),
            appliances=munch.Munch(dict(amount=23)),
            vGateways64=munch.Munch(dict(amount=24)),
            vGateways128=munch.Munch(dict(amount=25)),
            workstationAgents=munch.Munch(dict(amount=26)),
            serverAgents=munch.Munch(dict(amount=27)),
            cloudDrives=munch.Munch(dict(amount=28)),
            cloudDrivesLite=munch.Munch(dict(amount=29))
        ))
        plan = CteraPortalPlan()
        plan.parameters = dict(name='admin')
        plan._ctera_portal.plans.get = mock.MagicMock(return_value=munch.Munch(returned_dict))
        self.assertDictEqual(expected_user_dict, plan._get_plan())

    def test__get_user_doesnt_exist(self):
        plan = CteraPortalPlan()
        plan.parameters = dict(name='admin')
        plan._ctera_portal.plans.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=404)))
        self.assertIsNone(plan._get_plan())

    def test_ensure_present(self):
        for is_present in [True, False]:
            for change_attributes in [True, False]:
                self._test_ensure_present(is_present, change_attributes)

    @staticmethod
    def _test_ensure_present(is_present, change_attributes):
        current_attributes = dict(
            name='main',
            retention=[
                dict(policy_name='retainAll', duration=11),
                dict(policy_name='hourly', duration=12),
                dict(policy_name='daily', duration=13),
                dict(policy_name='weekly', duration=14),
                dict(policy_name='monthly', duration=15),
                dict(policy_name='quarterly', duration=16),
                dict(policy_name='yearly', duration=17),
                dict(policy_name='retainDeleted', duration=18)
            ],
            quotas=[
                dict(item_name='EV4', amount=21),
                dict(item_name='EV8', amount=22),
                dict(item_name='EV16', amount=23),
                dict(item_name='EV64', amount=24),
                dict(item_name='EV128', amount=25),
                dict(item_name='WA', amount=26),
                dict(item_name='SA', amount=27),
                dict(item_name='Share', amount=28),
                dict(item_name='Connect', amount=29)
            ]
        )
        desired_attributes = copy.deepcopy(current_attributes)
        if not is_present:
            expected_params = dict(
                retention={i['policy_name']: i['duration'] for i in desired_attributes['retention']},
                quotas={i['item_name']: i['amount'] for i in desired_attributes['quotas']}
            )
        elif change_attributes:
            desired_attributes['retention'][0]['duration'] = 45
            expected_params = dict(
                retention={i['policy_name']: i['duration'] for i in desired_attributes['retention']},
                quotas=None
            )
        plan = CteraPortalPlan()
        plan.parameters = desired_attributes
        plan._ensure_present(current_attributes if is_present else None)
        if is_present:
            if change_attributes:
                plan._ctera_portal.plans.modify.assert_called_with(desired_attributes['name'], **expected_params)
            else:
                plan._ctera_portal.plans.modify.assert_not_called()
        else:
            plan._ctera_portal.plans.add.assert_called_with(desired_attributes['name'], **expected_params)

    def test_ensure_absent(self):
        for is_present in [True, False]:
            self._test_ensure_absent(is_present)

    @staticmethod
    def _test_ensure_absent(is_present):
        name = 'main'
        plan = CteraPortalPlan()
        plan.parameters = dict(name=name)
        plan._ensure_absent(plan.parameters if is_present else None)
        if is_present:
            plan._ctera_portal.plans.delete.assert_called_once_with(name)
        else:
            plan._ctera_portal.plans.delete.assert_not_called()
