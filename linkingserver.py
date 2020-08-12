"""
Empty server that send the _bare_ minimum data to keep a minecraft client connected
"""
import logging
import random
import time
import json
from argparse import ArgumentParser
from copy import deepcopy

import config

from twisted.internet import reactor
from quarry.net.server import ServerFactory, ServerProtocol

from quarry.types.uuid import UUID

from prometheus import set_players_online, init_prometheus

class Protocol(ServerProtocol):
    def __init__(self, factory, remote_addr):
        self.uuid = UUID.from_offline_player('NotKatuen')

        self.forwarded_uuid = None
        self.forwarded_host = None
        self.version = None

        super(Protocol, self).__init__(factory, remote_addr)

    def packet_handshake(self, buff):
        buff2 = deepcopy(buff)
        super().packet_handshake(buff)

        p_protocol_version = buff2.unpack_varint()
        p_connect_host = buff2.unpack_string()

        if p_protocol_version == 578:
            from versions import Version_1_15

            self.version = Version_1_15(self)
        elif p_protocol_version == 736:
            from versions import Version_1_16

            self.version = Version_1_16(self)
        elif p_protocol_version == 751:
            from versions import Version_1_16_2

            self.version = Version_1_16_2(self)
        else:
            self.close("Unsupported Minecraft Version")

        # Bungeecord ip forwarding, ip/uuid is included in host string separated by \00s
        split_host = str.split(p_connect_host, "\00")

        if len(split_host) >= 3:
            host = split_host[1]
            online_uuid = split_host[2]

            self.forwarded_host = host
            self.forwarded_uuid = UUID.from_hex(online_uuid)

    def player_joined(self):
        # Overwrite with forwarded information if present
        if self.forwarded_uuid is not None:
            self.uuid = self.forwarded_uuid
            self.display_name_confirmed = True

        if self.forwarded_host is not None:
            self.connect_host = self.forwarded_host

        super().player_joined()

        set_players_online(len(self.factory.players))

        self.version.player_joined()
    def player_left(self):
        super().player_left()

        set_players_online(len(self.factory.players))

    def packet_chat_message(self, buff):
        self.version.packet_chat_message(buff)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-a", "--host", default="127.0.0.1", help="bind address")
    parser.add_argument("-p", "--port", default=25567, type=int, help="bind port")
    parser.add_argument("-m", "--max", default=65535, type=int, help="player count")
    parser.add_argument("-r", "--metrics", default=None, type=int, help="expose prometheus metrics on specified port")

    args = parser.parse_args()

    server_factory = ServerFactory()
    server_factory.protocol = Protocol
    server_factory.max_players = args.max
    server_factory.motd = "Linking Server"
    server_factory.online_mode = False
    server_factory.compression_threshold = 5646848

    metrics_port = args.metrics

    config.load_chunk_config()

    if metrics_port is not None:
        init_prometheus(metrics_port)

    server_factory.listen(args.host, args.port)
    print('Server started')
    print("Listening on {}:{}".format(args.host, args.port))
    reactor.run()
