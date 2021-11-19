import hmac
import json
import logging
import os
import sys

from argparse import ArgumentParser
from copy import deepcopy

from quarry.net.server import ServerFactory, ServerProtocol
from quarry.types.uuid import UUID
from twisted.internet import reactor

import linkingserver.config
from linkingserver.prometheus import set_players_online, init_prometheus

linking_secret = None

if getattr(sys, 'frozen', False):  # PyInstaller adds this attribute
    # Running in a bundle
    path = os.path.join(sys._MEIPASS, 'linkingserver')
else:
    # Running in normal Python environment
    path = os.path.dirname(__file__)

# Logging
logger = logging.getLogger('linkingserver')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(filename='linkingserver.log')
console_handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter('[%(asctime)s %(levelname)s]: [%(name)s] %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

class Protocol(ServerProtocol):
    def __init__(self, factory, remote_addr):
        from linkingserver.versions import Version_1_15, Version_1_16, Version_1_16_2, Version_1_17, Version_1_17_1, \
            Version_1_18pre4

        self.uuid = UUID.from_offline_player('NotKatuen')

        self.forwarded_uuid = None
        self.forwarded_host = None
        self.is_bedrock = False
        self.version = None
        self.versions = {
            578: Version_1_15,
            736: Version_1_16,
            751: Version_1_16_2,
            755: Version_1_17,
            756: Version_1_17_1,
            1073741876: Version_1_18pre4
        }

        super(Protocol, self).__init__(factory, remote_addr)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def packet_handshake(self, buff):
        buff2 = deepcopy(buff)
        super().packet_handshake(buff)

        p_protocol_version = buff2.unpack_varint()
        p_connect_host = buff2.unpack_string()

        # Bungeecord ip forwarding, ip/uuid is included in host string separated by \00s
        split_host = str.split(p_connect_host, "\00")

        if len(split_host) >= 3:
            # TODO: Should probably verify the encrypted data in some way.
            # Not important until something on this server uses uuids
            if split_host[1] == 'Geyser-Floodgate':
                self.is_bedrock = True

                host = split_host[4]
                online_uuid = split_host[5]
            elif split_host[1].startswith('^Floodgate^'):
                self.is_bedrock = True

                host = split_host[2]
                online_uuid = split_host[3]
            else:
                host = split_host[1]
                online_uuid = split_host[2]

            self.forwarded_host = host
            self.forwarded_uuid = UUID.from_hex(online_uuid)

        version = None

        for pv, v in self.versions.items():
            if p_protocol_version >= pv:
                version = v

        if version is not None:
            self.version = version(self, self.is_bedrock)
        else:
            self.close("Unsupported Minecraft Version")

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

    def packet_animation(self, buff):
        self.version.send_open_book()
        buff.discard()

    def packet_use_item(self, buff):
        self.version.send_open_book()
        buff.discard()

    def packet_held_item_change(self, buff):
        buff.discard()

        if self.version.is_bedrock:
            self.version.give_book()

    def packet_plugin_message(self, buff):
        channel = buff.unpack_string()
        data = buff.read()

        if channel != "proxydiscord:status":
            return

        payload = json.loads(data.decode(encoding="utf-8"))
        payload_hmac = payload.get("hmac")

        msg = "{0:d}{1:d}{2:s}".format(payload.get("status"), payload.get("bedrock"), payload.get("token"))
        calculated_hmac = hmac.new(key=str.encode(linking_secret, encoding="utf-8"),
                                   msg=str.encode(msg, encoding="utf-8"), digestmod="sha512")

        if calculated_hmac.hexdigest() != payload_hmac:
            self.logger.warn("Failed to validate plugin message for {}. Is the linking secret configured correctly?"
                             .format(self.display_name))
            return

        self.version.status_received(payload)


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

    if metrics_port is not None:
        init_prometheus(metrics_port)

    config = linkingserver.config.load_config()

    linking_secret = config['secret']

    server_factory.listen(args.host, args.port)
    logger.info('Server started')
    logger.info("Listening on {}:{}".format(args.host, args.port))
    reactor.run()
