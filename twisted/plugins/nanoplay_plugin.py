from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.internet import reactor
from twisted.application import service, strports
from nanoplay import PayloadProtocol, ControlProtocol, CustomServer, Player

class Options(usage.Options):
    optParameters = [
        ["payload", "p",
         "tcp:port=5000", "Endpoint to listen for files on"],
        ["control", "c",
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
        payload_service = strports.service(options["payload"],                                   
                                           CustomServer(PayloadProtocol, player))
        payload_service.setServiceParent(s)
        control_service = strports.service(options["control"],
                                           CustomServer(ControlProtocol, player))
        control_service.setServiceParent(s)
        return s


serviceMaker = NanoplayMaker()
