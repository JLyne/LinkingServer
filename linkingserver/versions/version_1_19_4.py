from linkingserver.versions import Version_1_19_3


class Version_1_19_4(Version_1_19_3):
    protocol_version = 762

    def send_spawn(self, effects=False):
        self.protocol.send_packet("spawn_position", self.protocol.buff_type.pack("iii", 0, 0, 0))

        self.protocol.send_packet("player_position_and_look",
                                  self.protocol.buff_type.pack("dddff?", 0, 2048, 0, 0.0, 0.0, 0b00000),
                                  self.protocol.buff_type.pack_varint(0)) # Remove dismount vehicle

    def get_written_book_id(self):
        return 1043
