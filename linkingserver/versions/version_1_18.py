from quarry.types.nbt import TagInt

from linkingserver.versions import Version_1_17_1
from linkingserver.protocol import Protocol


class Version_1_18(Version_1_17_1):
    protocol_version = 757
    chunk_format = '1.18'

    def __init__(self, protocol: Protocol, bedrock: False):
        super(Version_1_18, self).__init__(protocol, bedrock)

    def get_dimension_settings(self):
        settings = super().get_dimension_settings()

        settings['min_y'] = TagInt(-64)
        settings['height'] = TagInt(384)

        return settings

    def send_spawn(self):
        super().send_spawn()
        self.protocol.send_packet("player_abilities", self.protocol.buff_type.pack("bff", 7, 0.05, 0.1))

    def send_join_game(self):
        self.init_dimension_codec()

        self.protocol.send_packet("join_game",
                                  self.protocol.buff_type.pack("i?BB", 0, False, 1, 1),
                                  self.protocol.buff_type.pack_varint(2),
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack_string("rtgame:reset"),
                                  self.protocol.buff_type.pack_nbt(self.dimension_codec),
                                  self.protocol.buff_type.pack_nbt(self.current_dimension),
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack("q", 0),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack_varint(32),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("????", False, True, False, False))

