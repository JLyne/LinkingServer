import hmac
import json

from copy import deepcopy

from quarry.net.server import ServerProtocol
from quarry.types.uuid import UUID

from linkingserver.log import console_handler, file_handler, logger
from linkingserver.prometheus import set_players_online

versions = {}


class Protocol(ServerProtocol):
    linking_secret = None

    def __init__(self, factory, remote_addr):
        super(Protocol, self).__init__(factory, remote_addr)

        self.is_bedrock = False
        self.version = None

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def packet_handshake(self, buff):
        buff2 = deepcopy(buff)
        super().packet_handshake(buff)

        buff2.unpack_varint()
        p_connect_host = buff2.unpack_string()

        # Floodgate
        split_host = str.split(p_connect_host, "\00")

        if len(split_host) >= 2:
            # TODO: Should probably verify the encrypted data in some way.
            # Not important until something on this server uses uuids
            if split_host[1].startswith('^Floodgate^'):
                self.is_bedrock = True

                if self.factory.bungeecord_forwarding:
                    self.connect_host = split_host[2]
                    self.uuid = split_host[3]

        version = None

        # Select version handler
        for protocol_version, v in versions.items():
            if self.protocol_version >= protocol_version:
                version = v

        if version is not None:
            self.version = version(self, self.is_bedrock)
        else:
            self.close("Unsupported Minecraft Version")

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

    def configuration(self):
        self.data_packs.add_data_pack(self.version.get_data_pack())
        self.complete_configuration()


# Build dictionary of protocol version -> version class
# Local import to prevent circlular import issues
def build_versions():
    import linkingserver.versions

    for version in vars(linkingserver.versions).values():
        if hasattr(version, 'protocol_version') and version.protocol_version is not None:
            versions[version.protocol_version] = version
