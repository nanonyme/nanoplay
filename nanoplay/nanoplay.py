from twisted.internet import glib2reactor # for non-GUI apps
glib2reactor.install()
from zope.interface import implements
from twisted.python import log, usage
from twisted.plugin import IPlugin
from twisted.internet import reactor, defer, protocol, error
from twisted.application import service, strports
from twisted.protocols import basic
import os
import pygst
pygst.require("0.10")
import gst
import collections
import tempfile

def log_and_exit(fail):
    log.err(fail)
    reactor.stop()

class Player(object):
    def __init__(self, reactor):
        self.reactor = reactor
        self.queue = collections.deque()
        self.current = None
        self.player = gst.element_factory_make("playbin2", "player")
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        

    def play(self, file_obj):
        new = {"file_obj": file_obj, "deferred": defer.Deferred()}
        filepath = os.path.abspath(new["file_obj"].name)
        log.msg("Putting %s to queue" % filepath)
        self.queue.append(new)
        if self.current is None:
            self._do_play()
        return new["deferred"]


    def skip(self):
        self._do_stop()
        self._do_play()

    def kill(self):
        self._do_stop()
        while True:
            try:
                item = self.queue.popleft()
            except IndexError:
                break
            else:
                item["deferred"].callback(item["file_obj"])


    def _do_play(self):
        try:
            self.current = self.queue.popleft()
        except IndexError:
            pass
        else:
            filepath = os.path.abspath(self.current["file_obj"].name)
            print "Playing %s" % filepath
            self.player.set_property("uri", "file://" + filepath)
            self.player.set_state(gst.STATE_PLAYING)

    def _do_stop(self):
        if self.current is not None:
            self.player.set_state(gst.STATE_NULL)
            current, self.current = self.current, None
            current["deferred"].callback(current["file_obj"])

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self._do_stop()
            self._do_play()
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            log.msg("Error: %s" % err, debug)
            self.reactor.stop()

player = Player(reactor)


class PayloadProtocol(protocol.Protocol):
    def __init__(self):
        self.file_obj = tempfile.NamedTemporaryFile()

    def dataReceived(self, data):
        self.file_obj.write(data)
        self.file_obj.flush()

    def connectionLost(self, reason=error.ConnectionDone):
        d = self.factory.player.play(self.file_obj)
        d.addCallback(lambda f : f.close())
        protocol.Protocol.connectionLost(self, reason)

class ControlProtocol(basic.LineOnlyReceiver):
    delimiter = "\n"

    def lineReceived(self, line):
        log.msg("Control channel got %s" % line)
        command = line.strip().lower()
        reply = "Unrecognized command\n"
        if command == "skip":
            self.factory.player.skip()
            reply = "Ok\n"
        elif command == "kill":
            self.factory.player.kill()
            reply = "Ok\n"
        self.transport.write(reply)
        self.transport.loseConnection()



class CustomServer(protocol.ServerFactory):
    def __init__(self, protocol, player):
        self.protocol = protocol
        self.player = player

    def buildProtocol(self, addr):
        p = PayloadProtocol()
        p.factory = self
        return p


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
                                           CustomServer(PayloadProtocol, player))
        payload_service.setServiceParent(s)
        return s


serviceMaker = NanoplayMaker()
