from linkingserver.protocol import Protocol
from linkingserver.versions import Version_1_21_4


class Version_1_21_5(Version_1_21_4):
    protocol_version = 770

    def __init__(self, protocol: Protocol, bedrock: bool):
        super(Version_1_21_4, self).__init__(protocol, bedrock)

    def get_written_book_id(self):
        return 1153