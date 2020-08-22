import abc
import json

from quarry.types.uuid import UUID

from linkingserver import Protocol

class Version(object, metaclass=abc.ABCMeta):
    def __init__(self, protocol: Protocol):
        self.protocol = protocol
        self.uuid = UUID.from_offline_player('NotKatuen')

        self.version_name = None
        self.status_packet_received = False

        self.linking_status = None
        self.linking_token = None
        self.is_bedrock = None

    def player_joined(self):
        self.send_join_game()

        self.protocol.ticker.add_loop(100, self.send_keep_alive)  # Keep alive packets

        self.protocol.send_packet("player_position_and_look",
                             self.protocol.buff_type.pack("dddff?", 0, 0, 0, 0.0, 0.0, 0b00000),
                                    self.protocol.buff_type.pack_varint(0))

        self.protocol.ticker.add_delay(10, self.send_tablist)
        self.protocol.ticker.add_delay(20, self.status_timeout)

    def status_received(self, payload):
        self.status_packet_received = True
        self.linking_token = payload.get("token")
        self.linking_status = payload.get("status")
        self.is_bedrock = payload.get("bedrock")
        self.send_book()

    def send_tablist(self):
        self.protocol.send_packet("player_list_header_footer",
                         self.protocol.buff_type.pack_string(json.dumps({
                            "text": 'Gamers Online: ',
                            "extra": [
                                {
                                    "text": "123",
                                    "obfuscated": True,
                                    "color": "green"
                                },
                            ]
                        })),
                         self.protocol.buff_type.pack_string(json.dumps({"translate": ""})))

    def send_commands(self):
        commands = {
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

        self.protocol.send_packet('declare_commands', self.protocol.buff_type.pack_commands(commands))

    def status_timeout(self):
        if self.status_received is False:
            self.protocol.close("An unexpected error has occurred. Please try again later")

    def send_keep_alive(self):
        self.protocol.send_packet("keep_alive", self.protocol.buff_type.pack("Q", 0))

    @abc.abstractmethod
    def send_join_game(self):
        raise NotImplementedError('users must define send_join_game to use this base class')

    @abc.abstractmethod
    def send_book(self):
        raise NotImplementedError('users must define send_book to use this base class')

    @abc.abstractmethod
    def send_open_book(self):
        raise NotImplementedError('users must define send_open_book to use this base class')

