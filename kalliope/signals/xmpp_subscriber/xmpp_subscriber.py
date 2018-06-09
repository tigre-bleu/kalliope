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

        # we need to sort jid and attach synapses name to run to it
        list_clients_to_instantiate = self.get_list_clients_to_instantiate(self.list_synapses_with_xmpp)

        # now instantiate an XMPP client for each jid
        self.instantiate_xmpp_clients(list_clients_to_instantiate)


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

    @staticmethod
    def get_list_clients_to_instantiate(list_synapse_with_xmpp_subscriber):
        """
        return a list of jid object from the given list of synapse
        :param list_synapse_with_xmpp_subscriber: list of Synapse object
        :return: list of Jid
        """
        returned_list_of_clients = list()

        for synapse in list_synapse_with_xmpp_subscriber:
            for signal in synapse.signals:
                # check if the client exist in the list
                if not any(x["jid"] == signal.parameters["jid"] for x in returned_list_of_clients):
                    logger.debug("[Xmpp_subscriber] Create new client: %s" % signal.parameters["jid"])
                    # create a new Client object
                    synapses = list()
                    synapses.append(synapse)
                    returned_list_of_clients.append({"jid": signal.parameters["jid"], "password": signal.parameters["password"], "synapses": synapses})

        return returned_list_of_clients


    def instantiate_xmpp_clients(self, list_clients_to_instantiate):
        """
        Instantiate a XmppClient thread for each broker
        :param list_clients_to_instantiate: list of clients to run
        """
        for client in list_clients_to_instantiate:
            xmpp_client = XmppClient(jid=client["jid"], password=client["password"], synapses=client["synapses"], brain=self.brain)
            # Connect to the XMPP server and start processing XMPP stanzas.
            if xmpp_client.connect():
                # If you do not have the dnspython library installed, you will need
                # to manually specify the name of the server if it does not match
                # the one in the JID. For example, to use Google Talk you would
                # need to use:
                #
                # if xmpp.connect(('talk.google.com', 5222)):
                #     ...
                logger.debug("[XmppClient] Connecting " + client["jid"])
                xmpp_client.process()
                logger.debug("[XmppClient] Connected to " + client["jid"])
            else:
                logger.debug("[XmppClient] Unable to connect to " + client["jid"])
