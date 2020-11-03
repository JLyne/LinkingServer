import abc
import json

from quarry.types.uuid import UUID

from linkingserver import Protocol

class Version(object, metaclass=abc.ABCMeta):
    def __init__(self, protocol: Protocol, bedrock: False):
        self.protocol = protocol

        self.version_name = None
        self.status_packet_received = False

        self.linking_status = None
        self.linking_token = None
        self.is_bedrock = bedrock

    def player_joined(self):
        self.send_join_game()
        self.send_inventory()

        self.protocol.ticker.add_loop(100, self.send_keep_alive)  # Keep alive packets

        self.protocol.send_packet("player_position_and_look",
                             self.protocol.buff_type.pack("dddff?", 0, 2048, 0, 0.0, 0.0, 0b00000),
                                    self.protocol.buff_type.pack_varint(0))

        self.protocol.ticker.add_delay(10, self.send_tablist)
        self.protocol.ticker.add_delay(20, self.status_timeout)

    def status_received(self, payload):
        first_status = not self.status_packet_received

        self.status_packet_received = True
        self.linking_token = payload.get("token")
        self.linking_status = payload.get("status")

        if self.is_bedrock:
            if not first_status:
                self.send_respawn()

            self.send_world()
            self.send_book()
            self.protocol.ticker.add_delay(40, self.send_title)
        else :
            self.send_book()


    def send_tablist(self):
        self.protocol.send_packet("player_list_header_footer",
                         self.protocol.buff_type.pack_string(json.dumps({
                            "text": "\ue340\uf801\ue341\n\ue342\uf801\ue343"
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

    def send_world(self):
        raise NotImplementedError('users must define send_world to use this base class')

    def send_title(self):
        raise NotImplementedError('users must define send_title to use this base class')

    def send_respawn(self):
        raise NotImplementedError('users must define send_respawn to use this base class')

    @abc.abstractmethod
    def send_inventory(self):
        raise NotImplementedError('users must define send_inventory to use this base class')