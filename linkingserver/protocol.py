import hmac
import json
import random

from copy import deepcopy

from quarry.net.server import ServerProtocol
from quarry.types.uuid import UUID
from twisted.internet import defer

from linkingserver.log import console_handler, file_handler, logger
from linkingserver.prometheus import set_players_online

versions = {}


class Protocol(ServerProtocol):
    linking_secret = None
    bungee_forwarding = False
    velocity_forwarding = False
    velocity_forwarding_secret = None

    def __init__(self, factory, remote_addr):
        super(Protocol, self).__init__(factory, remote_addr)

        self.velocity_message_id = None
        self.is_bedrock = False
        self.version = None

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def packet_handshake(self, buff):
        buff2 = deepcopy(buff)
        super().packet_handshake(buff)

        buff2.unpack_varint()
        p_connect_host = buff2.unpack_string()

        if self.bungee_forwarding is True:
            # Bungeecord ip forwarding, ip/uuid is included in host string separated by \00s
            split_host = str.split(p_connect_host, "\00")

            if len(split_host) < 3:
                logger.warning("Invalid bungeecord forwarding data received from {}".format(self.remote_addr))
                self.close("Invalid bungeecord forwarding data")
                return

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

            self.connect_host = host
            self.uuid = UUID.from_hex(online_uuid)

            logger.info("Bungeecord: {}".format(self.uuid))

        version = None

        # Select version handler
        for protocol_version, v in versions.items():
            if self.protocol_version >= protocol_version:
                version = v

        if version is not None:
            self.version = version(self, self.is_bedrock)
        else:
            self.close("Unsupported Minecraft Version")

    def packet_login_start(self, buff):
        if self.login_expecting != 0:
            logger.warning("Unexpected login_start received from {}".format(self.remote_addr))
            self.close("Out-of-order login")
            return

        if self.velocity_forwarding is True:
            self.login_expecting = 2
            self.velocity_message_id = random.randint(0, 2147483647)
            self.send_packet("login_plugin_request",
                             self.buff_type.pack_varint(self.velocity_message_id),
                             self.buff_type.pack_string("velocity:player_info"),
                             b'')
            buff.read()
            return

        self.login_expecting = None
        self.display_name_confirmed = True
        self.display_name = buff.unpack_string()

        if self.protocol_version >= 759:  # 1.19
            if buff.unpack('?'):
                timestamp = buff.unpack("Q")
                key_length = buff.unpack_varint()
                key_bytes = buff.read(key_length)
                signature_length = buff.unpack_varint()
                signature = buff.read(signature_length)

        self.player_joined()

    # fixme: remove once quarry updated
    def switch_protocol_mode(self, mode):
        self.check_protocol_mode_switch(mode)

        if mode == "play":
            if self.factory.compression_threshold and self.protocol_version >= 47:
                # Send set compression
                self.send_packet(
                    "login_set_compression",
                    self.buff_type.pack_varint(
                        self.factory.compression_threshold))
                self.set_compression(self.factory.compression_threshold)

            # Send login success
            if self.protocol_version >= 759:
                self.send_packet(
                    "login_success",
                    self.buff_type.pack_uuid(self.uuid) +
                    self.buff_type.pack_string(self.display_name) +
                    self.buff_type.pack_varint(0))  # No properties
            elif self.protocol_version > 578:
                self.send_packet(
                    "login_success",
                    self.buff_type.pack_uuid(self.uuid) +
                    self.buff_type.pack_string(self.display_name))
            else:
                self.send_packet(
                    "login_success",
                    self.buff_type.pack_string(self.uuid.to_hex()) +
                    self.buff_type.pack_string(self.display_name))

            if self.protocol_version <= 5:
                def make_safe():
                    self.safe_kick.callback(None)
                    self.safe_kick = None

                def make_unsafe():
                    self.safe_kick = defer.Deferred()
                    self.ticker.add_delay(10, make_safe)

                make_unsafe()

        self.protocol_mode = mode


    def packet_login_plugin_response(self, buff):
        if self.login_expecting != 2 or self.protocol_mode != "login":
            logger.warning("Unexpected login_plugin_response received from {}".format(self.remote_addr))
            self.close("Out-of-order login")
            return

        message_id = buff.unpack_varint()
        successful = buff.unpack('b')

        if message_id != self.velocity_message_id:
            logger.warning("Unexpected login_plugin_response received from {}".format(self.remote_addr))
            self.close("Unexpected login_plugin_response")
            return

        if not successful or len(buff) == 0:
            logger.warning("Empty velocity forwarding response received from {}".format(self.remote_addr))
            self.close("Empty velocity forwarding response")
            return

        # Verify HMAC
        signature = buff.read(32)
        verify = hmac.new(key=str.encode(self.velocity_forwarding_secret), msg=deepcopy(buff).read(),
                          digestmod="sha256").digest()

        if verify != signature:
            logger.warning("Invalid velocity forwarding response received from {}".format(self.remote_addr))
            self.close("Invalid velocity forwarding response received")
            buff.read()
            return

        version = buff.unpack_varint()

        if version != 1:
            logger.warning("Unsupported velocity forwarding version received from {}".format(self.remote_addr))
            self.close("Unsupported velocity forwarding version")
            buff.read()
            return

        buff.unpack_string()  # Ip

        self.uuid = buff.unpack_uuid()
        self.display_name = buff.unpack_string()

        buff.read()  # Don't care about the rest

        self.login_expecting = None
        self.display_name_confirmed = True
        logger.info("Velocity: {} {}".format(self.display_name, self.uuid))
        self.player_joined()

    def player_joined(self):
        if self.uuid is None:
            self.uuid = UUID.from_offline_player(self.display_name)

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
        calculated_hmac = hmac.new(key=str.encode(self.linking_secret, encoding="utf-8"),
                                   msg=str.encode(msg, encoding="utf-8"), digestmod="sha512")

        if calculated_hmac.hexdigest() != payload_hmac:
            self.logger.warn("Failed to validate plugin message for {}. Is the linking secret configured correctly?"
                             .format(self.display_name))
            return

        self.version.status_received(payload)


# Build dictionary of protocol version -> version class
# Local import to prevent circlular import issues
def build_versions():
    import linkingserver.versions

    for version in vars(linkingserver.versions).values():
        if hasattr(version, 'protocol_version') and version.protocol_version is not None:
            versions[version.protocol_version] = version
