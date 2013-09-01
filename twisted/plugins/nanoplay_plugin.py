from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.internet import reactor
from twisted.application import service, strports
from nanoplay import PayloadProtocol, ControlProtocol, CustomServer, Player

class Options(usage.Options):
    optParameters = [
        ["payload-endpoint", "p",
         "tcp:port=5000", "Endpoint to listen for files on"],
        ["control-enpoint", "c",
         "tcp:port=5001", "Endpoint to listen for control commands on"]
        ]

class NanoplayMaker(object):
    implements(service.IServiceMaker, IPlugin)
    tapname = "nanoplay"
    description = "nanoplay, trivial music player"
    options = Options

    def makeService(self, options):
        """
        Construct a TCPServer from a factory defined in myproject.
        """
        player = Player(reactor)
        reactor.addSystemEventTrigger("before", "shutdown", player.kill)
        s = service.MultiService()
        payload_service = strports.service(options["payload-endpoint"],                                   
                                           CustomServer(PayloadProtocol, player))
        payload_service.setServiceParent(s)
        payload_service = strports.service(options["control-endpoint"],
                                           CustomServer(ControlProtocol, player))
        payload_service.setServiceParent(s)
        return s


serviceMaker = NanoplayMaker()
