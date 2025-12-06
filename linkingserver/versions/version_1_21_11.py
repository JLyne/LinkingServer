from linkingserver.protocol import Protocol
from linkingserver.versions import Version_1_21_9


class Version_1_21_11(Version_1_21_9):
    protocol_version = 1073742109

    def __init__(self, protocol: Protocol, bedrock: bool):
        super(Version_1_21_9, self).__init__(protocol, bedrock)

    def get_written_book_id(self):
        return 1221
