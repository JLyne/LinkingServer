from typing import Protocol


from linkingserver.versions import Version_1_20_2


class Version_1_20_3(Version_1_20_2):
    protocol_version = 765

    def __init__(self, protocol: Protocol, bedrock: False):
        super(Version_1_20_2, self).__init__(protocol, bedrock)

    def send_spawn(self):
        super().send_spawn()
        self.protocol.send_packet("change_game_state", self.protocol.buff_type.pack("Bf", 13, 0.0))  # Hide loading terrain screen

    def get_written_book_id(self):
        return 1086
