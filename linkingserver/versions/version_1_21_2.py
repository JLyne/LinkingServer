from quarry.types.namespaced_key import NamespacedKey

from linkingserver.protocol import Protocol
from linkingserver.versions import Version_1_21


class Version_1_21_2(Version_1_21):
    protocol_version = 768

    def __init__(self, protocol: Protocol, bedrock: bool):
        super(Version_1_21, self).__init__(protocol, bedrock)

    def send_join_game(self):
        dimension_registry = self.protocol.data_packs.get_registry(NamespacedKey.minecraft('dimension_type'))
        id = list(dimension_registry).index(NamespacedKey.minecraft('overworld'))

        self.protocol.send_packet("login",
                                  self.protocol.buff_type.pack("i?", 0, False),
                                  self.protocol.buff_type.pack_varint(2),
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack_string("rtgame:reset"),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack_varint(7),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("???", False, True, False),
                                  self.protocol.buff_type.pack_varint(id),
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack("qBb??", 0, 1, 1, False, False),
                                  self.protocol.buff_type.pack("?", False),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack_varint(64), # Sea level
                                  self.protocol.buff_type.pack("?", False))

    def send_spawn(self):
        self.protocol.send_packet("set_default_spawn_position", self.protocol.buff_type.pack("iii", 0, 0, 0))

        self.protocol.send_packet("player_position",
                                  self.protocol.buff_type.pack_varint(0), # Move to front
                                  self.protocol.buff_type.pack("ddddddffi", 0, 2048, 0, 0, 0, 0, 0.0, 0.0, # Add second vector for movement
                                                               0)) # Bitset instead of boolean

        self.protocol.send_packet("game_event", self.protocol.buff_type.pack("Bf", 13, 0.0))

    def send_open_book(self):
        self.protocol.send_packet("set_held_slot", self.protocol.buff_type.pack("b", 0)) # Renamed packet
        self.protocol.send_packet("open_book", self.protocol.buff_type.pack_varint(0))