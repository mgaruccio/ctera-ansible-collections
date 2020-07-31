trust_certificate = False

class AnsibleModuleMock():

    def __init__(self, _argument_spec, **_kwargs):
        self.params = dict(
            ctera_host='192.168.1.1',
            ctera_user='admin',
            ctera_https=True,
            ctera_port=None,
            ctera_password='password',
            ctera_trust_certificate=trust_certificate
        )
        self.fail_dict = {}
        self.exit_dict = {}

    def fail_json(self, **kwargs):
        for k, v in kwargs.items():
            self.fail_dict[k] = v

    def exit_json(self, **kwargs):
        for k, v in kwargs.items():
            self.exit_dict[k] = v


def mock_bases(test, klass):
    original_bases = klass.__bases__
    klass.__bases__ = (AnsibleModuleMock,)
    test.addCleanup(restore_bases, klass, original_bases)


def restore_bases(klass, bases):
    klass.__bases__ = bases
