import json
import logging
import socket
from threading import Thread

import sleekxmpp
from kalliope.core.SynapseLauncher import SynapseLauncher

logging.basicConfig()
logger = logging.getLogger("kalliope")


class XmppClient(Thread):

    def __init__(self, jid=None, password=None):
        """
        Class used to instantiate xmpp client
        Thread used to be non blocking when called from parent class
        :param jid: jid object
        :type jid: String
        :param password: password object
        :type password: String
        """
        super(XmppClient, self).__init__()
        self.jid = jid
        self.password = password

        if self.jid is not None and self.password is not None:
            logger.debug("[XmppClient] Jid and password are set")
            sleekxmpp.ClientXMPP.__init__(self, jid, password)
            self.add_event_handler("session_start", self.on_start)
            self.add_event_handler("message", self.on_message)

    def on_start(self, event):
        self.send_presence()
        self.get_roster()

    def on_message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            logger.debug(msg['from'].bare + ": " + msg['body'])
