# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Documentation fragment for CTERA (ctera)
    DOCUMENTATION = r'''
options:
  ctera_host:
    description: IP Address or FQDN of the CTERA Networks Host
    required: True
    type: str
  ctera_https:
    description: Connect to the Host using HTTPS
    type: bool
    default: True
  ctera_port:
    description: Connection port to the Host
    type: int
  ctera_user:
    description: User Name for communicating with the CTERA Networks Host
    required: True
    type: str
  ctera_password:
    description: Password of the user
    required: True
    type: str
  ctera_trust_certificate:
    description: Trust unverified certificates
    type: bool
    default: False

requirements:
  - A physical or virtual CTERA-Networks Gateway
  - Ansible 2.8
  - Python3 cterasdk. Install using 'pip install cterasdk'

'''
