#!/usr/bin/env python

# External modules
from twisted.internet import main
from twisted.internet import reactor
from twisted.internet import main, interfaces, reactor
from twisted.python import log, failure
from zope.interface import implementer
import os
from scapy.all import IP
import struct
import binascii


@implementer(interfaces.IReadDescriptor, interfaces.IPushProducer)
class TUNPacketProducer(object):

    def __init__(self, tunDevice, consumer=None):
        self.tunDevice    = tunDevice
        self.mtu          = tunDevice.mtu
        self.fd           = os.dup(tunDevice.fileno())

        consumer.registerProducer(self, streaming=True)
        self.consumer     = consumer

    def logPrefix(self):
        return 'TUNPacketProducer'

    # IPushProducer

    def pauseProducing(self):
        log.msg("pauseProducing")
        reactor.removeReader(self)

    def resumeProducing(self):
        log.msg("resumeProducing")
        reactor.addReader(self)

    def stopProducing(self):
        log.msg("stopProducing")

    # IReadDescriptor

    def connectionLost(self, reason):
        log.msg("connectionLost")
        self.stopProducing()
        self.consumer.unregisterProducer()
        self.tunDevice.close()
        self.tunDevice.down()
        return reason

    def fileno(self):
        return self.fd

    def doRead(self):
        log.msg("doRead")
        packet = self.tunDevice.read(self.tunDevice.mtu)
        self.consumer.write(packet)



