import json

from quarry.types.nbt import TagInt, TagRoot, TagCompound, TagLongArray

from versions import Version_1_16_2
from linkingserver import Protocol


class Version_1_17(Version_1_16_2):
    def __init__(self, protocol: Protocol, bedrock: False):
        super(Version_1_17, self).__init__(protocol, bedrock)
        self.version_name = '1.17'

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
                                  self.protocol.buff_type.pack_string(json.dumps({"text": "Read the Book"})))
        self.protocol.send_packet("set_title_time",
                                  self.protocol.buff_type.pack("iii", 10, 72000, 72000))

    def get_written_book_id(self):
        return 943

    def send_reset_world(self):
        data = [
            self.protocol.buff_type.pack_varint(0),
            b'',
            self.protocol.buff_type.pack_nbt(
                TagRoot({'': TagCompound({"MOTION_BLOCKING": TagLongArray(PackedArray.empty_height())})})),
            self.protocol.buff_type.pack_varint(1024),
        ]

        for i in range(1024):
            data.append(self.protocol.buff_type.pack_varint(127))

        data.append(self.protocol.buff_type.pack_varint(0))
        data.append(b'')
        data.append(self.protocol.buff_type.pack_varint(0))
        data.append(b'')

        for x in range(-8, 8):
            for y in range(-8, 8):
                self.protocol.send_packet("chunk_data", self.protocol.buff_type.pack("ii", x, y), *data)
