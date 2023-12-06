from quarry.types.chat import Message

from linkingserver.versions import Version_1_19_1


class Version_1_19_3(Version_1_19_1):
    protocol_version = 761

    def send_spawn(self):
        self.protocol.send_packet("spawn_position", self.protocol.buff_type.pack("iii", 0, 0, 0))
        super().send_spawn()

    def send_tablist(self):
        self.protocol.send_packet("player_list_header_footer",
                                  self.protocol.buff_type.pack_chat(Message("\n\ue300\n")),
                                  self.protocol.buff_type.pack_chat(Message("")))

        self.protocol.send_packet("player_list_item",
                                  self.protocol.buff_type.pack('B', 63),
                                  self.protocol.buff_type.pack_varint(1),
                                  self.protocol.buff_type.pack_uuid(self.protocol.uuid),
                                  self.protocol.buff_type.pack_string(self.protocol.display_name),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("?", False),  # False for no chat session info
                                  self.protocol.buff_type.pack_varint(1),
                                  self.protocol.buff_type.pack("?", True),  # Show in tab list
                                  self.protocol.buff_type.pack_varint(1),
                                  self.protocol.buff_type.pack("?", False))

    def get_written_book_id(self):
        return 1019
