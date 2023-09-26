from typing import Protocol


from linkingserver.versions import Version_1_20


class Version_1_20_2(Version_1_20):
    protocol_version = 764

    def __init__(self, protocol: Protocol, bedrock: False):
        super(Version_1_20, self).__init__(protocol, bedrock)

    def send_join_game(self):
        self.protocol.send_packet("join_game",
                                  self.protocol.buff_type.pack("i?", 0, False),
                                  self.protocol.buff_type.pack_varint(2),
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack_string("rtgame:reset"),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack_varint(7),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("???", False, True, False),  # Added is limited crafting
                                  self.protocol.buff_type.pack_string("minecraft:overworld"),  # Moved current dimension
                                  self.protocol.buff_type.pack_string("rtgame:linking"),  # Moved current world
                                  self.protocol.buff_type.pack("qBb??", 0, 1, 1, False, False),  # Moved hashed seed, current/prev gamemode
                                  self.protocol.buff_type.pack("?", False),
                                  self.protocol.buff_type.pack_varint(0))
