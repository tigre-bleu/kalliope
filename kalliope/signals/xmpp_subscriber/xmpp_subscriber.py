import logging
from threading import Thread

from kalliope.core import SignalModule, MissingParameter

from kalliope.core.ConfigurationManager import BrainLoader
from kalliope.signals.xmpp_subscriber.XmppClient import XmppClient

from kalliope.core import Utils

logging.basicConfig()
logger = logging.getLogger("kalliope")


class Xmpp_subscriber(SignalModule, Thread):

    def __init__(self, **kwargs):
        super(Xmpp_subscriber, self).__init__(**kwargs)
        Thread.__init__(self, name=Xmpp_subscriber)
        Utils.print_info('[Xmpp_subscriber] Starting manager')# variables
        self.list_synapses_with_xmpp = list(super(Xmpp_subscriber, self).get_list_synapse())
        self.jid = None
        self.password = None

    def run(self):
        logger.debug("[Xmpp_subscriber] Starting Xmpp_subscriber")

        # now instantiate an XMPP client
        xmpp_client = XmppClient(jid=self.jid, password=self.password)
        xmpp_client.start()

    @staticmethod
    def check_parameters(parameters):
        """
        overwrite method
        receive a dict of parameter from a xmpp_subscriber signal
        :param parameters: dict of xmpp_signal_parameters
        :return: True if parameters are valid
        """
        # check mandatory parameters
        mandatory_parameters = ["jid", "password"]
        if not all(key in parameters for key in mandatory_parameters):
            return False

        return True
