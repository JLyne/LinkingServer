from linkingserver.protocol import Protocol
from linkingserver.versions import Version_1_21_2


class Version_1_21_4(Version_1_21_2):
    protocol_version = 769

    def __init__(self, protocol: Protocol, bedrock: bool):
        super(Version_1_21_2, self).__init__(protocol, bedrock)

    def get_written_book_id(self):
        return 1142