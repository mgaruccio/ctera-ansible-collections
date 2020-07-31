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

from ansible_collections.ctera.ctera.plugins.module_utils.ctera_ansible_module import CteraAnsibleModule

try:
    from cterasdk import GlobalAdmin
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common


class PortalAnsibleModule(CteraAnsibleModule):
    default_argument_spec = {
        'tenant': dict(type='str')
    }

    def __init__(self, argument_spec, **kwargs):
        argument_spec.update(PortalAnsibleModule.default_argument_spec)
        super().__init__(argument_spec, **kwargs)
        self._ctera_host = GlobalAdmin(self.params['ctera_host'], port=self.params['ctera_port'], https=self.params['ctera_https'])

    def ctera_portal(self, login=True):
        if login:
            self.ctera_login()
        return self._ctera_host
