import json

from quarry.types.nbt import TagInt

from linkingserver.versions import Version_1_18_2


class Version_1_19(Version_1_18_2):
    protocol_version = 759

    def send_join_game(self):
        self.init_dimension_codec()

        self.protocol.send_packet("join_game",
                                  self.protocol.buff_type.pack("i?Bb", 0, False, 1, 1),
                                  self.protocol.buff_type.pack_varint(2),
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack_string("rtgame:reset"),
                                  self.protocol.buff_type.pack_nbt(self.dimension_codec),
                                  self.protocol.buff_type.pack_string("minecraft:overworld"),  # Current dimension is now a string
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack("q", 0),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack_varint(7),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("?????", False, True, False, False, False))  # Extra False for not providing a death location

    def send_respawn(self):
        self.protocol.send_packet("respawn",
                                  self.protocol.buff_type.pack_string("minecraft:overworld"),  # Current dimension is now a string
                                  self.protocol.buff_type.pack_string("rtgame:reset"),
                                  self.protocol.buff_type.pack("qBB", 0, 1, 1),
                                  self.protocol.buff_type.pack("????", False, False, True, False))

        self.protocol.send_packet("respawn",
                                  self.protocol.buff_type.pack_string("minecraft:overworld"),  # Current dimension is now a string
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack("qBB", 0, 1, 1),
                                  self.protocol.buff_type.pack("????", False, False, True, False))

    def get_dimension_settings(self):
        settings = super().get_dimension_settings()

        # New dimension settings
        settings['monster_spawn_block_light_limit'] = TagInt(0)
        settings['monster_spawn_light_level'] = TagInt(0)

        return settings

    def send_tablist(self):
        self.protocol.send_packet("player_list_header_footer",
                                  self.protocol.buff_type.pack_string(json.dumps({
                                      "text": "\n\ue300\n"
                                  })),
                                  self.protocol.buff_type.pack_string(json.dumps({"translate": ""})))

        self.protocol.send_packet("player_list_item",
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack_varint(1),
                                  self.protocol.buff_type.pack_uuid(self.protocol.uuid),
                                  self.protocol.buff_type.pack_string(self.protocol.display_name),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack_varint(1),
                                  self.protocol.buff_type.pack_varint(1),
                                  self.protocol.buff_type.pack("??", False, False))  # Extra false for unsigned profile

    def get_written_book_id(self):
        return 986