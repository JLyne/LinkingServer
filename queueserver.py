"""
Empty server that send the _bare_ minimum data to keep a minecraft client connected
"""
import logging
import random
import time
from argparse import ArgumentParser
from copy import deepcopy

from quarry.types.buffer import Buffer

import config
from chunk import Chunk

from twisted.internet import reactor
from quarry.net.server import ServerFactory, ServerProtocol

from quarry.types.uuid import UUID

from voting import entry_json, entry_navigation_json

chunks = list()
voting_mode = False

class StoneWallProtocol(ServerProtocol):
    def __init__(self, factory, remote_addr):
        self.uuid = UUID.from_offline_player('NotKatuen')
        self.viewpoint_id = 999

        self.current_chunk = None
        self.current_viewpoint = None
        self.raining = False

        self.player_spawned = False
        self.viewpoint_spawned = False
        self.viewpoint_used = False

        self.last_click = time.time()

        self.forwarded_uuid = None
        self.forwarded_host = None

        super(StoneWallProtocol, self).__init__(factory, remote_addr)

    def packet_handshake(self, buff):
        buff2 = deepcopy(buff)
        super().packet_handshake(buff)

        buff2.unpack_varint()
        p_connect_host = buff2.unpack_string()

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

        # Sent init packets
        self.send_packet("join_game",
                         self.buff_type.pack("iBqiB", 0, 3, 0, 0, 0),
                         self.buff_type.pack_string("flat"),
                         self.buff_type.pack_varint(6),
                         self.buff_type.pack("??", False, True))

        self.ticker.add_loop(100, self.send_keep_alive)  # Keep alive packets

        if voting_mode:
            self.current_chunk = chunks[0]
        else:
            self.current_chunk = random.choice(chunks)

        self.send_chunk()

    # Cycle through viewpoints when player clicks
    def packet_animation(self, buff):
        buff.unpack_varint()

        now = time.time()

        # Prevent spam
        if now - self.last_click > 0.5:
            self.last_click = now
            self.next_viewpoint()

    # Handle /next and /orev commands in voting mode
    def packet_chat_message(self, buff):
        if voting_mode is False:
            return

        message = buff.unpack_string()

        if message == "/prev":
            self.previous_chunk()
        elif message == "/next":
            self.next_chunk()

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

        if voting_mode:
            self.send_packet('chat_message',
                         self.buff_type.pack_string(entry_json(chunks.index(self.current_chunk) + 1, len(chunks))),
                         self.buff_type.pack("b", 1))

        # Credits
        self.send_packet('chat_message',
                         self.buff_type.pack_string( self.current_chunk.credit_json()),
                         self.buff_type.pack("b", 1))

        if voting_mode:
            self.send_packet('chat_message',
                         self.buff_type.pack_string(entry_navigation_json(self.uuid, voting_secret)),
                         self.buff_type.pack("b", 1))

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

    def next_viewpoint(self):
        count = len(self.current_chunk.viewpoints)

        if count is 0:
            return
        elif self.current_viewpoint < count - 1:
            self.current_viewpoint += 1
            self.send_viewpoint()
        elif voting_mode:
            self.current_viewpoint = 0
            self.send_viewpoint()
        else:
            self.random_chunk()

    def reset_chunk(self):
        self.player_spawned = False
        self.viewpoint_spawned = False
        self.viewpoint_used = False
        self.raining = False

        self.send_packet("respawn", self.buff_type.pack("iBq", 1, 3, 0), self.buff_type.pack_string("flat"))
        self.send_packet("respawn", self.buff_type.pack("iBq", 0, 3, 0), self.buff_type.pack_string("flat"))
        self.send_chunk()

    def next_chunk(self):
        if len(chunks) > 1:
            index = chunks.index(self.current_chunk)
            next_index = index + 1 if index < len(chunks) - 1 else 0
            self.current_chunk = chunks[next_index]

        self.reset_chunk()
        self.send_chunk()

    def previous_chunk(self):
        if len(chunks) > 1:
            index = chunks.index(self.current_chunk)
            prev_index = index - 1 if index > 0 else len(chunks) - 1
            self.current_chunk = chunks[prev_index]

        self.reset_chunk()
        self.send_chunk()

    def random_chunk(self):
        if len(chunks) > 1:
            current_chunk = self.current_chunk

            while current_chunk == self.current_chunk:
                self.current_chunk = random.choice(chunks)

        self.reset_chunk()
        self.send_chunk()

    def send_keep_alive(self):
        self.send_packet("keep_alive", self.buff_type.pack("Q", 0))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-a", "--host", default="127.0.0.1", help="bind address")
    parser.add_argument("-p", "--port", default=25567, type=int, help="bind port")
    parser.add_argument("-m", "--max", default=65535, type=int, help="player count")
    parser.add_argument("-v", "--voting", action='store_true',
                        help="puts server in 'voting' mode - shows entry counts and prev/next buttons")
    parser.add_argument("-s", "--secret", type=str,
                        help="Shared secret for voting url HMAC")

    args = parser.parse_args()

    server_factory = ServerFactory()
    server_factory.protocol = StoneWallProtocol
    server_factory.max_players = args.max
    server_factory.motd = "Queue Server"
    server_factory.online_mode = False
    server_factory.compression_threshold = 5646848

    voting_mode = args.voting
    voting_secret = args.secret

    chunks = config.load_chunk_config()

    if voting_mode is True and voting_secret is None:
        logging.getLogger('main').error("You must provide a secret (-s) to use voting mode. Exiting.")
        exit(1)

    if len(chunks) is 0:
        logging.getLogger('main').error("No chunks defined. Exiting.")
        exit(1)

    server_factory.listen(args.host, args.port)
    print('Server started')
    print("Listening on {}:{}".format(args.host, args.port))
    reactor.run()

