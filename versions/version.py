import abc
import time
import json
import random

from quarry.types.uuid import UUID

import config
from linkingserver import Protocol

class Version(object, metaclass=abc.ABCMeta):
    def __init__(self, protocol: Protocol):
        self.protocol = protocol
        self.uuid = UUID.from_offline_player('NotKatuen')
        self.viewpoint_id = 999

        self.current_chunk = None
        self.raining = False

        self.player_spawned = False
        self.viewpoint_spawned = False
        self.viewpoint_used = False

        self.version_name = None

    def player_joined(self):
        self.send_join_game()

        self.protocol.ticker.add_loop(100, self.send_keep_alive)  # Keep alive packets
        self.current_chunk = random.choice(config.chunks[self.version_name])

        self.send_chunk()
        self.send_commands()

        self.protocol.ticker.add_delay(10, self.send_tablist)

    # Handle /spawn and /reset commands
    def packet_chat_message(self, buff):
        message = buff.unpack_string()
        now = time.time()

        if message == "/spawn" or message == "/hub":
            if now - self.last_command < 0.5:
                return

            self.send_spawn()
        elif message == "/reset":
            if now - self.last_command < 2:
                return

            self.reset_world()
        else:
            return

        self.last_command = time.time()

    def send_chunk(self):
        self.current_viewpoint = 0
        self.send_viewpoint()

        # Chunk packets
        for packet in  self.current_chunk.packets:
            self.protocol.send_packet(packet.get('type'), packet.get('packet'))


        # Start/stop rain as necessary
        if self.current_chunk.weather == 'rain':
            if self.raining is False:
                self.protocol.send_packet('change_game_state', self.protocol.buff_type.pack("Bf", 2, 0))
                self.raining = True
        elif self.raining is True:
            self.protocol.send_packet('change_game_state', self.protocol.buff_type.pack("Bf", 1, 0))
            self.raining = False

        # Time of day
        self.protocol.send_packet('time_update',
                         self.protocol.buff_type.pack("Qq", 0,
                                             # Cycle
                                             self.current_chunk.time  if self.current_chunk.cycle is True
                                             else (0 - self.current_chunk.time)))

    def send_viewpoint(self):
        viewpoint =  self.current_chunk.viewpoints[self.current_viewpoint]
        x = viewpoint.get('x')
        z = viewpoint.get('z')

        # Player hasn't spawned yet
        # Spawn them outside chunk to prevent movement
        if self.player_spawned is False:
                self.protocol.send_packet("player_position_and_look",
                             self.protocol.buff_type.pack("dddff?", 128.0, 128, -128, 0.0, 0.0, 0b00000),
                                    self.protocol.buff_type.pack_varint(0))

                self.player_spawned = True

        # Teleport and spectate viewpoint entity
        if self.viewpoint_spawned is False:
            self.spawn_viewpoint_entity(viewpoint)

            self.viewpoint_spawned = True
        else :
            self.protocol.send_packet('entity_teleport', self.protocol.buff_type.pack_varint(self.viewpoint_id),
                             self.protocol.buff_type.pack("dddbbb",
                                    x,
                                    viewpoint.get('y'),
                                    z,
                                    viewpoint.get('yaw_256'),
                                    viewpoint.get('pitch'),
                                    0))

            self.protocol.send_packet('entity_head_look',
                             self.protocol.buff_type.pack_varint(self.viewpoint_id),
                             self.protocol.buff_type.pack("b", viewpoint.get('yaw_256')))

        if self.viewpoint_used is False:
            self.protocol.send_packet('camera', self.protocol.buff_type.pack_varint(self.viewpoint_id))
            self.viewpoint_used = True

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
                    "name": "link",
                    "executable": True,
                    "redirect": None,
                    "children": dict(),
                    "suggestions": None
                },
            },
        }

        self.protocol.send_packet('declare_commands', self.protocol.buff_type.pack_commands(commands))

    def send_keep_alive(self):
        self.protocol.send_packet("keep_alive", self.protocol.buff_type.pack("Q", 0))

    @abc.abstractmethod
    def send_join_game(self):
        raise NotImplementedError('users must define send_join_game to use this base class')

    @abc.abstractmethod
    def send_respawn(self):
        raise NotImplementedError('users must define send_respawn to use this base class')

    @abc.abstractmethod
    def spawn_viewpoint_entity(self, viewpoint):
        raise NotImplementedError('users must define spawn_viewpoint_entity to use this base class')
