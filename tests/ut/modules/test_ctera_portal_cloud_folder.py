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
    from cterasdk import CTERAException, portal_types
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

from ansible_collections.ctera.ctera.plugins.modules.ctera_portal_cloud_folder import CteraPortalCloudFolder
import tests.ut.mocks.ctera_portal_base_mock as ctera_portal_base_mock
from tests.ut.base import BaseTest


class TestCteraPortalFolderGroup(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_portal_base_mock.mock_bases(self, CteraPortalCloudFolder)

    def test__execute(self):
        for is_present in [True, False]:
            self._test__execute(is_present)

    @staticmethod
    def _test__execute(is_present):
        cloud_folder = CteraPortalCloudFolder()
        cloud_folder.parameters = dict(state='present' if is_present else 'absent')
        cloud_folder._get_cloud_folder = mock.MagicMock(return_value=dict())
        cloud_folder._ensure_present = mock.MagicMock()
        cloud_folder._ensure_absent = mock.MagicMock()
        cloud_folder._execute()
        if is_present:
            cloud_folder._ensure_present.assert_called_once_with(mock.ANY)
            cloud_folder._ensure_absent.assert_not_called()
        else:
            cloud_folder._ensure_absent.assert_called_once_with(mock.ANY)
            cloud_folder._ensure_present.assert_not_called()

    def test_get_cloud_folder_exists(self):
        expected_cf_dict = dict(
            name='folder_name',
            owner=dict(name='admin'),
            group='group_name'
        )
        returned_object = munch.Munch(
            dict(
                name=expected_cf_dict['name'],
                group='objs/13/portal/FoldersGroup/%s' % expected_cf_dict['group'],
                owner='objs/12/portal/PortalUser/%s' % expected_cf_dict['owner']['name']
            )
        )
        cloud_folder = CteraPortalCloudFolder()
        cloud_folder.parameters = dict(name=expected_cf_dict['name'], owner=expected_cf_dict['owner'])
        cloud_folder._ctera_portal.cloudfs.find = mock.MagicMock(return_value=returned_object)
        self.assertDictEqual(expected_cf_dict, cloud_folder._get_cloud_folder())

    def test__get_cloud_folder_doesnt_exist(self):
        cloud_folder = CteraPortalCloudFolder()
        cloud_folder.parameters = dict(
            name='folder_name',
            owner=dict(name='admin'),
            group='group_name'
        )
        cloud_folder._ctera_portal.cloudfs.find = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=404)))
        self.assertIsNone(cloud_folder._get_cloud_folder())

    def test_ensure_present(self):
        for is_present in [True, False]:
            for change_attributes in [True, False]:
                self._test_ensure_present(is_present, change_attributes)

    @staticmethod
    def _test_ensure_present(is_present, change_attributes):
        current_attributes = dict(
            name='folder_name',
            owner=dict(name='admin'),
            group='group_name',
            winacls=True
        )
        desired_attributes = copy.deepcopy(current_attributes)
        if change_attributes:
            desired_attributes['owner']['name'] = 'Tester'
        cloud_folder = CteraPortalCloudFolder()
        cloud_folder.parameters = desired_attributes
        cloud_folder._ensure_present(current_attributes if is_present else None)
        if is_present:
            cloud_folder._ctera_portal.cloudfs.mkdir.assert_not_called()
        else:
            cloud_folder._ctera_portal.cloudfs.mkdir.assert_called_with(
                desired_attributes['name'],
                desired_attributes['group'],
                portal_types.UserAccount(desired_attributes['owner']['name']),
                winacls=True
            )

    def test_ensure_absent(self):
        for is_present in [True, False]:
            self._test_ensure_absent(is_present)

    @staticmethod
    def _test_ensure_absent(is_present):
        parameters = dict(
            name='folder_name',
            owner=dict(name='admin'),
            group='group_name',
            winacls=True
        )
        cloud_folder = CteraPortalCloudFolder()
        cloud_folder.parameters = parameters
        cloud_folder._ensure_absent(cloud_folder.parameters if is_present else None)
        if is_present:
            cloud_folder._ctera_portal.cloudfs.delete.assert_called_once_with(
                parameters['name'],
                portal_types.UserAccount(parameters['owner']['name']),
            )
        else:
            cloud_folder._ctera_portal.cloudfs.delete.assert_not_called()
