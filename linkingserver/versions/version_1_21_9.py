from linkingserver.protocol import Protocol
from linkingserver.versions import Version_1_21_7


class Version_1_21_9(Version_1_21_7):
    protocol_version = 773

    def __init__(self, protocol: Protocol, bedrock: bool):
        super(Version_1_21_7, self).__init__(protocol, bedrock)

    def get_written_book_id(self):
        return 1217

    def send_spawn(self):
        self.protocol.send_packet("set_default_spawn_position",
                             self.protocol.buff_type.pack_global_position("rtgame:linking", 0, 0, 0) # Now global position
                             + self.protocol.buff_type.pack('ff', 0, 0)) # Added pitch

        self.protocol.send_packet("player_position",
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("ddddddffi", 0, 2048, 0, 0, 0, 0, 0.0, 0.0,
                                                               0))

        self.protocol.send_packet("game_event", self.protocol.buff_type.pack("Bf", 13, 0.0))