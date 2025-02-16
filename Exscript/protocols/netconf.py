import tempfile
from ncclient import manager
from ncclient.xml_ import to_ele
from ncclient.operations.rpc import RPCReply
from ncclient.transport.errors import AuthenticationError

from .protocol import Protocol


def get_tempfile(data):
    f = tempfile.NamedTemporaryFile()
    f.write(bytes(data, "utf-8"))
    return f

class Netconf(Protocol):

    """
    The netconf protocol adapter, based on ncclient.
    """

    def __init__(self, **kwargs):
        Protocol.__init__(self, **kwargs)
        self.sock = None
        self.manager = None
        self.shell = None
        self.account = None
        self.cancel = False


    def autoinit(self):
        pass


    def _ncclient_connect_and_login(self):
        kwargs = {}
        key_file = None
        if self.account and hasattr(self.account, "name") and self.account.name:
            # username is required
            kwargs["username"] = self.account.name
            if hasattr(self.account, "key") and self.account.key:
                key_file = get_tempfile(self.account.key)
                kwargs["key_filename"] = key_file.name
            elif hasattr(self.account, "password") and self.account.password:
                kwargs["password"] = self.account.password
        m = manager.connect(
            host=self.host, 
            port=self.port, 
            hostkey_verify=False, 
            **kwargs
        )
        if key_file:
            try:
                self.account.key_file.close()
            except FileNotFoundError:
                pass
        return m


    def _connect_hook(self, hostname, port):
        """
        Netconf requires authentication to connect
        We try to connect without an account,
        but do nothing if authentication is required
        """
        self.host = hostname
        self.port = port or 830
        try:
            self.manager = self._ncclient_connect_and_login()
        except AuthenticationError:
            self.manager = None
        return True


    def _get_response(self, data):
        if isinstance(data, RPCReply):
            self.response = data.xml
        else:
            self.response = str(data)
        # Send signals to subscribers.
        self.data_received_event(self.response + '\n')


    def _dispatch(self, data, ignore_result=False):
        xml_data = to_ele(data)
        rpc_reply = self.manager.dispatch(to_ele(xml_data))
        self._get_response(rpc_reply)
        return None if ignore_result else self.response


    def login(self, account=None, app_account=None, flush=True):
        if self.manager:
            return
        self.account = account
        self.manager = self._ncclient_connect_and_login()


    def send(self, data):
        return self._dispatch(data, ignore_result=True)
    

    def execute(self, command, *args, **kwargs):
        result = self._dispatch(command, ignore_result=False)
        return 0, result
    

    def close(self, force=False):
        self.manager.close_session()