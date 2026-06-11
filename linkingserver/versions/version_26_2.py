from quarry.types.namespaced_key import NamespacedKey

from linkingserver.protocol import Protocol
from linkingserver.versions import Version_26_1


class Version_26_2(Version_26_1):
    protocol_version = 1073742145

    def __init__(self, protocol: Protocol, bedrock: bool):
        super(Version_26_1, self).__init__(protocol, bedrock)

    def send_join_game(self):
        dimension_registry = self.protocol.data_packs.get_registry(NamespacedKey.minecraft('dimension_type'))
        id = list(dimension_registry).index(NamespacedKey.minecraft('overworld'))

        self.protocol.send_packet("login",
                                  self.protocol.buff_type.pack("i?", 830, False),
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
                                  self.protocol.buff_type.pack_varint(64),
                                  self.protocol.buff_type.pack("?", True), # Enable online mode
                                  self.protocol.buff_type.pack("?", False))

    def get_written_book_id(self):
        return 1251
