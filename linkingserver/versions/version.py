import abc
from pathlib import Path
from typing import Optional

from quarry.types.data_pack import DataPack

from linkingserver.config import books
from linkingserver.protocol import Protocol

parent_folder = Path(__file__).parent.parent


class Version(object, metaclass=abc.ABCMeta):
    protocol_version = None

    def __init__(self, protocol: Protocol, bedrock: False):
        self.protocol = protocol

        self.status_packet_received = False

        self.linking_status = None
        self.linking_token = None
        self.is_bedrock = bedrock

        self.written_book_id = self.get_written_book_id()

    def player_joined(self):
        self.send_join_game()
        self.send_inventory()
        self.send_spawn()

        self.protocol.ticker.add_loop(100, self.send_keep_alive)  # Keep alive packets
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
            self.give_book()
            self.protocol.ticker.add_delay(40, self.send_title)
        else:
            self.give_book()

    def status_timeout(self):
        if self.status_packet_received is False:
            self.protocol.close("An unexpected error has occurred. Please try again later")

    def send_world(self):
        self.send_spawn()

        # Clear geyser chunk cache from previous server
        if self.is_bedrock:
            self.send_reset_world()

        if self.is_bedrock:  # Current versions of geyser seem to ignore the time sometimes. Send repeatedly for now.
            self.protocol.ticker.add_loop(100, self.send_time)
        else:
            self.send_time()

    def give_book(self):
        if self.linking_status == 1:
            nbt = books['unlinked'].nbt(self.linking_token, self.is_bedrock)
        elif self.linking_status == 2:
            nbt = books['unverified'].nbt(self.linking_token, self.is_bedrock)
        else:
            return

        self.send_book(nbt)

    def get_data_pack(self) -> Optional[DataPack]:
        return None

    @abc.abstractmethod
    def send_join_game(self):
        raise NotImplementedError('send_join_game must be defined to use this base class')

    @abc.abstractmethod
    def send_spawn(self):
        raise NotImplementedError('send_spawn must be defined to use this base class')

    @abc.abstractmethod
    def send_respawn(self):
        raise NotImplementedError('send_respawn must be defined to use this base class')

    @abc.abstractmethod
    def send_reset_world(self):
        raise NotImplementedError('send_reset_world must be defined to use this base class')

    @abc.abstractmethod
    def send_keep_alive(self):
        raise NotImplementedError('send_keep_alive must be defined to use this base class')

    @abc.abstractmethod
    def send_time(self):
        raise NotImplementedError('send_time must be defined to use this base class')

    @abc.abstractmethod
    def send_title(self):
        raise NotImplementedError('send_title must be defined to use this base class')

    @abc.abstractmethod
    def send_commands(self):
        raise NotImplementedError('send_commands must be defined to use this base class')

    @abc.abstractmethod
    def send_tablist(self):
        raise NotImplementedError('send_tablist must be defined to use this base class')

    @abc.abstractmethod
    def send_inventory(self):
        raise NotImplementedError('send_inventory must be defined to use this base class')

    @abc.abstractmethod
    def get_written_book_id(self):
        raise NotImplementedError('get_written_book_id must be defined to use this base class')

    @abc.abstractmethod
    def send_book(self, nbt):
        raise NotImplementedError('send_book must be defined to use this base class')

    @abc.abstractmethod
    def send_open_book(self):
        raise NotImplementedError('send_open_book must be defined to use this base class')
