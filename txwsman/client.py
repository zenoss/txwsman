#!/usr/bin/env python
from utils import ConnectionInfo, _StringProtocol, _get_url_and_headers, create_request_sender
from twisted.internet import defer, reactor
import uuid
import logging
from lxml import etree
from cStringIO import StringIO

log = logging.getLogger('zen.wsman.Client')
log.setLevel(level=logging.DEBUG)

class Client(object):

    def __init__(self, hostname, username, password, port, scheme, auth_type):
        self._hostname = hostname
        self._auth_type = auth_type
        self._username = username
        self._password = password
        self._scheme = scheme
        self._port = port
        self._keytab = ''
        self._connectiontype = 'Keep-Alive'
        self._conn_info = ConnectionInfo(
                    self._hostname,
                    self._auth_type,
                    self._username,
                    self._password,
                    self._scheme,
                    self._port,
                    self._connectiontype,
                    self._keytab)

        self._url = "{c.scheme}://{c.hostname}:{c.port}/wsman".format(c=self._conn_info)

    @defer.inlineCallbacks
    def send_request(self, request, **kwargs):
        s=create_request_sender(self._conn_info)
        proto = _StringProtocol()
        resp = yield s.send_request(request,
                                     uuid=str(uuid.uuid4()),
                                     **kwargs)
        resp.deliverBody(proto)
        xml_str = yield proto.d

        try:
            tree = etree.parse(StringIO(xml_str))
            xml_str = etree.tostring(tree, pretty_print=True)
            log.debug(xml_str)
        except:
            log.debug('Could not prettify response XML: "{0}"'.format(xml_str))

        defer.returnValue(xml_str)

    def find_context(self, xml_str):
        resp_tree = etree.parse(StringIO(xml_str))

        # Strip the namespaces
        root=resp_tree.getroot()
        for elem in root.getiterator():
            i = elem.tag.find('}')
            if i >= 0:
               elem.tag = elem.tag[i+1:]

        try:
            context = resp_tree.xpath('//EnumerationContext/text()')[0]
        except Exception:
            context = None

        return context

    @defer.inlineCallbacks
    def pull(self, **kwargs):
        results = yield self.send_request('pull', resource_uri=self._url, **kwargs)
        defer.returnValue(results)

    @defer.inlineCallbacks
    def enumerate(self, **kwargs):
        results = yield self.send_request('enumerate', resource_uri=self._url, **kwargs)
        context = self.find_context(results)
        while context:
            pull = yield self.pull(context=context,**kwargs)
            context = self.find_context(pull)
            print pull
        defer.returnValue(results)

if __name__ == "__main__":

    logging.basicConfig()

    def stop_reactor():
        if reactor.running:
            reactor.stop()

    @defer.inlineCallbacks
    def enumerate_test():
        client = Client('10.100.40.178',
                        'root',
                        'calvin',
                        port='443',
                        scheme='https',
                        auth_type='basic')
        results = yield client.enumerate(ClassName='DCIM_ComputerSystems')
        import pdb;pdb.set_trace()
        stop_reactor()

    reactor.callWhenRunning(enumerate_test)
    reactor.run()



