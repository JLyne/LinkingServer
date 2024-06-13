from linkingserver.protocol import Protocol
from linkingserver.versions import Version_1_20_5


class Version_1_21(Version_1_20_5):
    protocol_version = 767

    def __init__(self, protocol: Protocol, bedrock: bool):
        super(Version_1_21, self).__init__(protocol, bedrock)
