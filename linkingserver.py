"""
Empty server that send the _bare_ minimum data to keep a minecraft client connected
"""
import logging
import random
import time
import json
from argparse import ArgumentParser
from copy import deepcopy

import config

from twisted.internet import reactor
from quarry.net.server import ServerFactory, ServerProtocol

from quarry.types.uuid import UUID

from prometheus import set_players_online, init_prometheus

chunks = list()

class StoneWallProtocol(ServerProtocol):
    def __init__(self, factory, remote_addr):
        self.uuid = UUID.from_offline_player('NotKatuen')
        self.viewpoint_id = 999

        self.current_chunk = None
        self.raining = False

        self.player_spawned = False
        self.viewpoint_spawned = False
        self.viewpoint_used = False

        self.forwarded_uuid = None
        self.forwarded_host = None

        super(StoneWallProtocol, self).__init__(factory, remote_addr)

    def packet_handshake(self, buff):
        buff2 = deepcopy(buff)
        super().packet_handshake(buff)

        p_protocol_version = buff2.unpack_varint()
        p_connect_host = buff2.unpack_string()

        if p_protocol_version != 578:
            self.close("Please use 1.15.2")

        # Bungeecord ip forwarding, ip/uuid is included in host string separated by \00s
        split_host = str.split(p_connect_host, "\00")

        if len(split_host) >= 3:
            host = split_host[1]
            online_uuid = split_host[2]

            self.forwarded_host = host
            self.forwarded_uuid = UUID.from_hex(online_uuid)

    def player_joined(self):
        # Overwrite with forwarded information if present
        if self.forwarded_uuid is not None:
            self.uuid = self.forwarded_uuid
            self.display_name_confirmed = True

        if self.forwarded_host is not None:
            self.connect_host = self.forwarded_host

        super().player_joined()

        set_players_online(len(self.factory.players))

        # Sent init packets
        self.send_packet("join_game",
                         self.buff_type.pack("iBqiB", 0, 3, 0, 0, 0),
                         self.buff_type.pack_string("flat"),
                         self.buff_type.pack_varint(6),
                         self.buff_type.pack("??", False, True))

        self.ticker.add_loop(100, self.send_keep_alive)  # Keep alive packets
        self.current_chunk = random.choice(chunks)

        self.send_chunk()
        self.send_commands()

        self.ticker.add_delay(10, self.send_tablist)

    def player_left(self):
        super().player_left()

        set_players_online(len(self.factory.players))

    def send_chunk(self):
        self.current_viewpoint = 0
        self.send_viewpoint()

        # Chunk packets
        for packet in  self.current_chunk.packets:
            self.send_packet(packet.get('type'), packet.get('packet'))


        # Start/stop rain as necessary
        if self.current_chunk.weather == 'rain':
            if self.raining is False:
                self.send_packet('change_game_state', self.buff_type.pack("Bf", 2, 0))
                self.raining = True
        elif self.raining is True:
            self.send_packet('change_game_state', self.buff_type.pack("Bf", 1, 0))
            self.raining = False

        # Time of day
        self.send_packet('time_update',
                         self.buff_type.pack("Qq", 0,
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
                self.send_packet("player_position_and_look",
                             self.buff_type.pack("dddff?", 128.0, 128, -128, 0.0, 0.0, 0b00000),
                                    self.buff_type.pack_varint(0))

                self.player_spawned = True

        # Teleport and spectate viewpoint entity
        if self.viewpoint_spawned is False:
            self.send_packet(
                'spawn_mob',
                self.buff_type.pack_varint(self.viewpoint_id),
                self.buff_type.pack_uuid(self.uuid),
                self.buff_type.pack_varint(62),
                self.buff_type.pack("dddbbbhhh",
                                    x,
                                    viewpoint.get('y'),
                                    z,
                                    viewpoint.get('yaw_256'),
                                    viewpoint.get('pitch'),
                                    viewpoint.get('yaw_256'), 0, 0, 0))

            self.viewpoint_spawned = True
        else :
            self.send_packet('entity_teleport', self.buff_type.pack_varint(self.viewpoint_id),
                             self.buff_type.pack("dddbbb",
                                    x,
                                    viewpoint.get('y'),
                                    z,
                                    viewpoint.get('yaw_256'),
                                    viewpoint.get('pitch'),
                                    0))

            self.send_packet('entity_head_look',
                             self.buff_type.pack_varint(self.viewpoint_id),
                             self.buff_type.pack("b", viewpoint.get('yaw_256')))

        if self.viewpoint_used is False:
            self.send_packet('camera', self.buff_type.pack_varint(self.viewpoint_id))
            self.viewpoint_used = True

    def send_tablist(self):
        self.send_packet("player_list_header_footer",
                         self.buff_type.pack_string(json.dumps({
                            "text": 'Gamers Online: ',
                            "extra": [
                                {
                                    "text": "123",
                                    "obfuscated": True,
                                    "color": "green"
                                },
                            ]
                        })),
                         self.buff_type.pack_string(json.dumps({"translate": ""})))

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

        self.send_packet('declare_commands', self.buff_type.pack_commands(commands))

    def send_keep_alive(self):
        self.send_packet("keep_alive", self.buff_type.pack("Q", 0))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-a", "--host", default="127.0.0.1", help="bind address")
    parser.add_argument("-p", "--port", default=25567, type=int, help="bind port")
    parser.add_argument("-m", "--max", default=65535, type=int, help="player count")
    parser.add_argument("-r", "--metrics", default=None, type=int, help="expose prometheus metrics on specified port")

    args = parser.parse_args()

    server_factory = ServerFactory()
    server_factory.protocol = StoneWallProtocol
    server_factory.max_players = args.max
    server_factory.motd = "Linking Server"
    server_factory.online_mode = False
    server_factory.compression_threshold = 5646848

    metrics_port = args.metrics

    chunks = config.load_chunk_config()

    if len(chunks) is 0:
        logging.getLogger('main').error("No chunks defined. Exiting.")
        exit(1)

    if metrics_port is not None:
        init_prometheus(metrics_port)

    server_factory.listen(args.host, args.port)
    print('Server started')
    print("Listening on {}:{}".format(args.host, args.port))
    reactor.run()
