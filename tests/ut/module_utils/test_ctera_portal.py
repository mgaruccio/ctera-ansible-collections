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
except ImportError:  # pragma: no cover
    pass

import ansible_collections.ctera.ctera.plugins.module_utils.ctera_ansible_module as ctera_ansible_module
import ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal as ctera_portal
from tests.ut.mocks import ansible_module_mock
from tests.ut.base import BaseTest


class TestCteraPortal(BaseTest):  #pylint: disable=too-many-public-methods

    def setUp(self):
        super().setUp()
        ansible_module_mock.mock_bases(self, ctera_ansible_module.CteraAnsibleModule)

        self.portal_class_mock = self.patch_call("ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal.GlobalAdmin")
        self.portal_object_mock = self.portal_class_mock.return_value

        self.ansible_return_value_class_mock = self.patch_call(
            "ansible_collections.ctera.ctera.plugins.module_utils.ctera_ansible_module.ctera_common.AnsibleReturnValue"
        )
        self.ansible_return_value_object_mock = self.ansible_return_value_class_mock.return_value

    def test_no_cterasdk(self):
        cterasdk_imp_err = "Failed to import"
        self.patch_call("ansible_collections.ctera.ctera.plugins.module_utils.ctera_ansible_module.ctera_common.HAS_CTERASDK", new=False)
        self.patch_call("ansible_collections.ctera.ctera.plugins.module_utils.ctera_ansible_module.ctera_common.CTERASDK_IMP_ERR", new=cterasdk_imp_err)
        portal_ansible_module = ctera_portal.PortalAnsibleModule(dict())
        self.assertDictEqual(portal_ansible_module.fail_dict, dict(msg=mock.ANY, exception=cterasdk_imp_err))

    def test_ctera_portal_with_login(self):
        self.portal_object_mock.login = mock.MagicMock(return_value=None)
        portal_ansible_module = ctera_portal.PortalAnsibleModule(dict())
        self.portal_class_mock.assert_called_once_with('192.168.1.1', https=True, port=None)
        portal_ansible_module.ctera_portal()
        self.portal_object_mock.login.assert_called_once_with('admin', 'password')

    def test_ctera_portal_login_failed(self):
        self.portal_object_mock.login = mock.MagicMock(side_effect=CTERAException())
        portal_ansible_module = ctera_portal.PortalAnsibleModule(dict())
        self.portal_class_mock.assert_called_once_with('192.168.1.1', https=True, port=None)
        portal_ansible_module.ctera_portal()
        self.portal_object_mock.login.assert_called_once_with('admin', 'password')

    def test_ctera_portal_no_login(self):
        self.portal_object_mock.login = mock.MagicMock(return_value=None)
        portal_ansible_module = ctera_portal.PortalAnsibleModule(dict())
        self.portal_class_mock.assert_called_once_with('192.168.1.1', https=True, port=None)
        portal_ansible_module.ctera_portal(login=False)
        self.portal_object_mock.login.assert_not_called()
