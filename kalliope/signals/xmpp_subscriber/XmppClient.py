import json
import logging
import socket
from threading import Thread

import sleekxmpp
from kalliope.core.SynapseLauncher import SynapseLauncher
from kalliope.core.ConfigurationManager import SettingLoader

logging.basicConfig()
logger = logging.getLogger("kalliope")


class XmppClient(Thread, sleekxmpp.ClientXMPP):

    def __init__(self, jid=None, password=None, synapses=None, brain=None):
        """
        Class used to instantiate xmpp client
        Thread used to be non blocking when called from parent class
        :param jid: jid object
        :type jid: String
        :param password: password object
        :type password: String
        """
        super(XmppClient, self).__init__()
        logger.debug("[XmppClient] Initialization")
        self.brain = brain
        self.synapses = synapses

        sl = SettingLoader()
        self.settings = sl.settings

        if jid is not None and password is not None:
            logger.debug("[XmppClient] Jid is " + jid + " and password is set")
            sleekxmpp.ClientXMPP.__init__(self, jid, password)
            self.add_event_handler("session_start", self.on_start)
            self.add_event_handler("message", self.on_message)
        else:
            logger.debug("[XmppClient] Jid and password are not set")

    def on_start(self, event):
        self.send_presence()
        self.get_roster()

    def on_message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            logger.debug("[XmppClient] Message received from " + msg['from'].bare + ": " + msg['body'])
            # run each synapse
            for synapse in self.synapses:
                logger.debug("[XmppClient] start synapse name %s" % synapse.name)
                overriding_parameter_dict = dict()
                overriding_parameter_dict["xmpp_subscriber_message"] = msg['body']
                SynapseLauncher.start_synapse_by_list_name([synapse.name],
                                                       brain=self.brain,
                                                       overriding_parameter_dict=overriding_parameter_dict)
            SynapseLauncher.run_matching_synapse_from_order(msg['body'],
                                                        self.brain,
                                                        self.settings,
                                                        is_api_call=True)
