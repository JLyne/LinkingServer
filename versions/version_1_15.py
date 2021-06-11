import json

from quarry.types.nbt import TagCompound, TagRoot

from versions import Version

from linkingserver import Protocol


class Version_1_15(Version):
    def __init__(self, protocol: Protocol, bedrock: False):
        super(Version_1_15, self).__init__(protocol, bedrock)
        self.version_name = '1.15'

        self.commands = {
            "name": None,
            "suggestions": None,
            "type": "root",
            "executable": True,
            "redirect": None,
            "children": {
                "link": {
                    "type": "literal",
                    "name": "unlink",
                    "executable": True,
                    "redirect": None,
                    "children": dict(),
                    "suggestions": None
                },
            },
        }

    def send_join_game(self):
        self.protocol.send_packet("join_game",
                                  self.protocol.buff_type.pack("iBqiB", 0, 3, 0, 0, 0),
                                  self.protocol.buff_type.pack_string("default"),
                                  self.protocol.buff_type.pack_varint(16),
                                  self.protocol.buff_type.pack("??", False, True))

    def send_spawn(self):
        self.protocol.send_packet("player_position_and_look",
                                  self.protocol.buff_type.pack("dddff?", 0, 2048, 0, 0.0, 0.0, 0b00000),
                                  self.protocol.buff_type.pack_varint(0))

    def send_reset_world(self):
        data = [
            self.protocol.buff_type.pack_varint(1),
            self.protocol.buff_type.pack('l', 0),
            self.protocol.buff_type.pack_nbt(TagRoot({'': TagCompound({})})),
            self.protocol.buff_type.pack_varint(1024),
        ]

        for i in range(0, 1024):
            data.append(self.protocol.buff_type.pack_varint(127))

        data.append(self.protocol.buff_type.pack_varint(0))
        data.append(self.protocol.buff_type.pack_varint(0))

        for x in range(-8, 8):
            for y in range(-8, 8):
                self.protocol.send_packet("chunk_data", self.protocol.buff_type.pack("ii", x, y), *data)

    def send_keep_alive(self):
        self.protocol.send_packet("keep_alive", self.protocol.buff_type.pack("Q", 0))

    def send_time(self):
        self.protocol.send_packet("time_update", self.protocol.buff_type.pack("ll", 0, -18000))

    def send_title(self):
        self.protocol.send_packet("title",
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack_string(json.dumps({"text": "Read the Book"})))
        self.protocol.send_packet("title",
                                  self.protocol.buff_type.pack_varint(3),
                                  self.protocol.buff_type.pack("iii", 10, 72000, 72000))

    def send_commands(self):
        self.protocol.send_packet('declare_commands', self.protocol.buff_type.pack_commands(self.commands))

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
                                  self.protocol.buff_type.pack_varint(0))

    def send_inventory(self):
        data = [
            self.protocol.buff_type.pack('Bh', 0, 46)
        ]

        for i in range(0, 46):
            data.append(self.protocol.buff_type.pack('?', False))

        self.protocol.send_packet('window_items', *data)

    def get_written_book_id(self):
        return 759

    def send_book(self, nbt):
        self.protocol.send_packet("set_slot", self.protocol.buff_type.pack("bh?", 0, 36, True),
                                  self.protocol.buff_type.pack_varint(self.written_book_id),
                                  self.protocol.buff_type.pack("b", 1),
                                  self.protocol.buff_type.pack_nbt(nbt))

        self.send_open_book()

    def send_open_book(self):
        self.protocol.send_packet("held_item_change", self.protocol.buff_type.pack("b", 0))
        self.protocol.send_packet("open_book", self.protocol.buff_type.pack_varint(0))
