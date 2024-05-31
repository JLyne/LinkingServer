from quarry.types.namespaced_key import NamespacedKey

from linkingserver.book import Book
from linkingserver.protocol import Protocol
from linkingserver.versions import Version_1_20_3


class Version_1_20_5(Version_1_20_3):
    protocol_version = 766

    def __init__(self, protocol: Protocol, bedrock: bool):
        super(Version_1_20_5, self).__init__(protocol, bedrock)

    def send_join_game(self):
        dimension_registry = self.protocol.data_packs.get_registry(NamespacedKey.minecraft('dimension_type'))
        dimension = dimension_registry.get(NamespacedKey.minecraft('overworld'))

        self.protocol.send_packet("join_game",
                                  self.protocol.buff_type.pack("i?", 0, False),
                                  self.protocol.buff_type.pack_varint(2),
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack_string("rtgame:reset"),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack_varint(7),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("???", False, True, False),
                                  self.protocol.buff_type.pack_varint(dimension['id']),  # Now varint
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack("qBb??", 0, 1, 1, False, False),
                                  self.protocol.buff_type.pack("?", False),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("?", False))  # Disable secure chat

    def send_respawn(self):
        dimension_registry = self.protocol.data_packs.get_registry(NamespacedKey.minecraft('dimension_type'))
        dimension = dimension_registry.get(NamespacedKey.minecraft('overworld'))

        self.protocol.send_packet("respawn",
                                  self.protocol.buff_type.pack_varint(dimension['id']), # Now varint
                                  self.protocol.buff_type.pack_string("rtgame:reset"),
                                  self.protocol.buff_type.pack("qBB", 0, 1, 1),
                                  self.protocol.buff_type.pack("???", False, False, False),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("b", 0))

        self.protocol.send_packet("respawn",
                                  self.protocol.buff_type.pack_varint(dimension['id']), # Now varint
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack("qBB", 0, 1, 1),
                                  self.protocol.buff_type.pack("???", False, False, False),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("b", 0))

    def send_book(self, book: Book):
        data = book.structured_data(self.linking_token, self.is_bedrock)

        self.protocol.send_packet("set_slot",
                                  self.protocol.buff_type.pack("b", 0),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("h", 36),
                                  self.protocol.buff_type.pack_slot(self.written_book_id, 1, data))

        self.send_open_book()

    def get_written_book_id(self):
        return 1092
