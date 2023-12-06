from quarry.types.chat import Message
from quarry.types.nbt import TagInt, TagRoot, TagCompound

from linkingserver.versions import Version_1_16_2
from linkingserver.protocol import Protocol


class Version_1_17(Version_1_16_2):
    protocol_version = 755

    def __init__(self, protocol: Protocol, bedrock: False):
        super(Version_1_17, self).__init__(protocol, bedrock)

    def get_dimension_settings(self):
        settings = super().get_dimension_settings()

        settings['min_y'] = TagInt(0)
        settings['height'] = TagInt(256)

        return settings

    def send_spawn(self):
        self.protocol.send_packet("player_position_and_look",
                                  self.protocol.buff_type.pack("dddff?", 0, 2048, 0, 0.0, 0.0, 0b00000),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("?", True))

    def send_title(self):
        self.protocol.send_packet("set_title_text",
                                  self.protocol.buff_type.pack_chat(Message("Read the Book")))
        self.protocol.send_packet("set_title_time",
                                  self.protocol.buff_type.pack("iii", 10, 72000, 72000))

    def get_written_book_id(self):
        return 943

    def send_reset_world(self):
        data = [
            self.protocol.buff_type.pack_nbt(TagRoot({'': TagCompound({})})),  # Heightmap
            self.protocol.buff_type.pack_varint(0),  # Data size
            self.protocol.buff_type.pack_varint(0),  # Block entity count
            self.protocol.buff_type.pack("?", True),  # Trust edges
            self.protocol.buff_type.pack_varint(0),  # Sky light mask
            self.protocol.buff_type.pack_varint(0),  # Block light mask
            self.protocol.buff_type.pack_varint(0),  # Empty sky light mask
            self.protocol.buff_type.pack_varint(0),  # Empty block light mask
            self.protocol.buff_type.pack_varint(0),  # Sky light array count
            self.protocol.buff_type.pack_varint(0),  # Block light array count
        ]

        for x in range(-8, 8):
            for y in range(-8, 8):
                self.protocol.send_packet("chunk_data", self.protocol.buff_type.pack("ii", x, y), *data)
