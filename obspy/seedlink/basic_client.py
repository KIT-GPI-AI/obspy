# -*- coding: utf-8 -*-
"""
SeedLink request client for ObsPy.

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from future.builtins import *  # NOQA @UnusedWildImport

import warnings

from obspy import Stream
from obspy.seedlink.slclient import SLClient, SLPacket
from obspy.seedlink.client.seedlinkconnection import SeedLinkConnection


class Client(object):
    """
    SeedLink request client.

    This client is intended for requests of specific, finite time windows.
    To work with continuous realtime data streams please see
    :class:`~obspy.seedlink.slclient.SLClient` and
    :class:`~obspy.seedlink.easyseedlink.EasySeedLinkClient`.

    :type server: str
    :param server: Server name or IP address to connect to (e.g.
        "localhost", "rtserver.ipgp.fr")
    :type port: int
    :param port: Port at which the seedlink server is operating (default is
        `18000`).
    :type timeout: float
    :param timeout: Network timeout for low-level network connection in
        seconds.
    :type debug: bool
    :param debug: Switches on debugging output.
    """
    def __init__(self, server, port=18000, timeout=20, debug=False):
        """
        Initializes the SeedLink request client.
        """
        self.timeout = timeout
        self.debug = debug
        self._slclient = SLClient(loglevel=debug and "DEBUG" or "CRITICAL")
        self._server_url = "%s:%i" % (server, port)

    def _connect(self):
        """
        Open new connection to seedlink server.
        """
        self._slclient.slconn = SeedLinkConnection()
        self._slclient.slconn.setSLAddress(self._server_url)
        self._slclient.slconn.netto = self.timeout

    def get_waveform(self, network, station, location, channel, starttime,
                     endtime):
        """
        Request waveform data from the seedlink server.

        >>> from obspy import UTCDateTime
        >>> client = Client('rtserver.ipgp.fr')
        >>> t = UTCDateTime() - 3600
        >>> client.get_waveform("G", "FDF", "00", "BHZ", t, t + 5)  # NOQA # doctest: +ELLIPSIS
        <obspy.core.stream.Stream object at 0x...>

        :type network: str
        :param network: Network code. No wildcards supported.
        :type station: str
        :param station: Station code. No wildcards supported.
        :type location: str
        :param location: Location code. No wildcards supported.
        :type channel: str
        :param channel: Channel code. No wildcards supported.
        :type starttime: :class:`~obspy.core.utcdatetime.UTCDateTime`
        :param starttime: Start time of requested time window.
        :type endtime: :class:`~obspy.core.utcdatetime.UTCDateTime`
        :param endtime: End time of requested time window.
        """
        if len(location) > 2:
            msg = ("Location code ('%s') only supports a maximum of 2 "
                   "characters.") % location
            raise ValueError(msg)
        elif len(location) == 1:
            msg = "Single character location codes are untested."
            warnings.warn(msg)
        if location:
            loccha = "%2s%3s" % (location, channel)
        else:
            loccha = channel
        seedlink_id = "%s_%s:%s" % (network, station, loccha)
        self._slclient.multiselect = seedlink_id
        self._slclient.begin_time = starttime
        self._slclient.end_time = endtime
        self._connect()
        self._slclient.initialize()
        self.stream = Stream()
        self._slclient.run(packet_handler=self._packet_handler)
        stream = self.stream
        stream.trim(starttime, endtime)
        self.stream = None
        return stream

    def _packet_handler(self, count, slpack):
        """
        Custom packet handler that accumulates all waveform packets in a
        stream.
        """
        # check if not a complete packet
        if slpack is None or (slpack == SLPacket.SLNOPACKET) or \
                (slpack == SLPacket.SLERROR):
            return False

        # get basic packet info
        type_ = slpack.getType()
        if self.debug:
            print(type_)

        # process INFO packets here
        if type_ == SLPacket.TYPE_SLINF:
            if self.debug:
                print(SLPacket.TYPE_SLINF)
            return False
        elif type_ == SLPacket.TYPE_SLINFT:
            if self.debug:
                print("Complete INFO:" + self.slconn.getInfoString())
            return False

        # process packet data
        trace = slpack.getTrace()
        if trace is None:
            if self.debug:
                print("Blockette contains no trace")
            return False

        # new samples add to the main stream which is then trimmed
        self.stream += trace
        self.stream.merge(-1)
        return False


if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)