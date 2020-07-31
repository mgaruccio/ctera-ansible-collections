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

import unittest.mock as mock

try:
    from cterasdk import CTERAException
    from cterasdk import config as ctera_config
except ImportError:  # pragma: no cover
    pass

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_ansible_module as ctera_ansible_module
from tests.ut.mocks import ansible_module_mock
from tests.ut.base import BaseTest


class TestCteraAnsibleModule(BaseTest):  #pylint: disable=too-many-public-methods

    def setUp(self):
        super().setUp()
        ansible_module_mock.mock_bases(self, ctera_ansible_module.CteraAnsibleModule)
        self.ansible_return_value_class_mock = self.patch_call(
            "ansible_collections.ctera.ctera.plugins.module_utils.ctera_ansible_module.ctera_common.AnsibleReturnValue"
        )
        self.ansible_return_value_object_mock = self.ansible_return_value_class_mock.return_value

    def test_no_cterasdk(self):
        cterasdk_imp_err = "Failed to import"
        self.patch_call("ansible_collections.ctera.ctera.plugins.module_utils.ctera_ansible_module.ctera_common.HAS_CTERASDK", new=False)
        self.patch_call("ansible_collections.ctera.ctera.plugins.module_utils.ctera_ansible_module.ctera_common.CTERASDK_IMP_ERR", new=cterasdk_imp_err)
        ansible_module = ctera_ansible_module.CteraAnsibleModule(dict())
        self.assertDictEqual(ansible_module.fail_dict, dict(msg=mock.ANY, exception=cterasdk_imp_err))

    @staticmethod
    def test_ctera_portal_logout():
        ansible_module = ctera_ansible_module.CteraAnsibleModule(dict())
        ansible_module._ctera_host = mock.MagicMock()  # pylint: disable=protected-access
        ansible_module._ctera_host.logout = mock.MagicMock(return_value=None)  # pylint: disable=protected-access
        ansible_module.ctera_logout()
        ansible_module._ctera_host.logout.assert_called_once_with()  # pylint: disable=protected-access

    def test_ctera_return_value(self):
        ansible_module = ctera_ansible_module.CteraAnsibleModule(dict())
        ansible_return_value = ansible_module.ctera_return_value()
        self.assertEqual(self.ansible_return_value_object_mock, ansible_return_value)

    def test_ctera_exit(self):
        for has_failed in [True, False]:
            self._test_ctera_exit(has_failed)

    def _test_ctera_exit(self, has_failed):
        self.ansible_return_value_object_mock.has_failed.return_value = has_failed
        expected_dict = dict(msg='Success')
        self.ansible_return_value_object_mock.as_dict.return_value = expected_dict
        ansible_module = ctera_ansible_module.CteraAnsibleModule(dict())
        ansible_module.ctera_exit()
        if has_failed:
            self.assertDictEqual(ansible_module.exit_dict, {})
            self.assertDictEqual(ansible_module.fail_dict, expected_dict)
        else:
            self.assertDictEqual(ansible_module.exit_dict, expected_dict)
            self.assertDictEqual(ansible_module.fail_dict, {})

    def test_trust_certificate(self):
        for trust in [True, False]:
            self._test_trust_certificate(trust)

    def _test_trust_certificate(self, trust):
        ansible_module_mock.trust_certificate = trust
        ctera_ansible_module.CteraAnsibleModule(dict())
        self.assertEqual(ctera_config.http['ssl'], 'Trust' if trust else 'Consent')
