from linkingserver.versions import Version_1_17
from linkingserver.server import Protocol


class Version_1_17_1(Version_1_17):
    protocol_version = 756

    def __init__(self, protocol: Protocol, bedrock: False):
        super(Version_1_17, self).__init__(protocol, bedrock)

    def send_inventory(self):
        data = [
            self.protocol.buff_type.pack('B', 0),
            self.protocol.buff_type.pack_varint(0),
            self.protocol.buff_type.pack_varint(46),
        ]

        for i in range(0, 46):
            data.append(self.protocol.buff_type.pack('?', False))

        data.append(self.protocol.buff_type.pack('?', False))
        self.protocol.send_packet('window_items', *data)

    def send_book(self, nbt):
        self.protocol.send_packet("set_slot", self.protocol.buff_type.pack("b", 0),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("h?", 36, True),
                                  self.protocol.buff_type.pack_varint(self.written_book_id),
                                  self.protocol.buff_type.pack("b", 1),
                                  self.protocol.buff_type.pack_nbt(nbt))
#
        self.send_open_book()

