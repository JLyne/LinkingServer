from linkingserver.protocol import Protocol
from linkingserver.versions import Version_1_21_5


class Version_1_21_6(Version_1_21_5):
    protocol_version = 771

    def __init__(self, protocol: Protocol, bedrock: bool):
        super(Version_1_21_5, self).__init__(protocol, bedrock)

    def get_written_book_id(self):
        return 1171