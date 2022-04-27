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

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.ctera.ctera.plugins.module_utils import ctera_common

try:
    from cterasdk import CTERAException, tojsonstr, config
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class CteraAnsibleModule(AnsibleModule):

    default_argument_spec = {
        'ctera_host': dict(type='str', required=True),
        'ctera_https': dict(type='bool', required=False, default=True),
        'ctera_port': dict(type='int', required=False),
        'ctera_user': dict(type='str', required=True),
        'ctera_password': dict(type='str', required=True, no_log=True),
        'ctera_trust_certificate': dict(type='bool', required=False, default=False)
    }

    def __init__(self, argument_spec, **kwargs):
        argument_spec.update(CteraAnsibleModule.default_argument_spec)
        super().__init__(argument_spec, **kwargs)
        if not ctera_common.HAS_CTERASDK:
            self.fail_json(msg=missing_required_lib('CTERASDK'), exception=ctera_common.CTERASDK_IMP_ERR)
        config.http['ssl'] = 'Trust' if self.params['ctera_trust_certificate'] else 'Consent'
        self._ctera_return_value = ctera_common.AnsibleReturnValue()
        self._ctera_host = None

    def ctera_login(self):
        try:
            self._ctera_host.login(self.params['ctera_user'], self.params['ctera_password'])
        except CTERAException as error:
            self._ctera_return_value.failed().msg('Login failed. Exception: %s' % tojsonstr(error, False))
            self.ctera_exit()

    def ctera_logout(self):
        self._ctera_host.logout()

    def ctera_return_value(self):
        return self._ctera_return_value

    def ctera_exit(self):
        if self._ctera_return_value.has_failed():
            self.fail_json(**self._ctera_return_value.as_dict())
        else:
            self.exit_json(**self._ctera_return_value.as_dict())
