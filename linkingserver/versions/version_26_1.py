from linkingserver.protocol import Protocol
from linkingserver.versions import Version_1_21_11


class Version_26_1(Version_1_21_11):
    protocol_version = 775

    def __init__(self, protocol: Protocol, bedrock: bool):
        super(Version_1_21_11, self).__init__(protocol, bedrock)

    def get_written_book_id(self):
        return 1222