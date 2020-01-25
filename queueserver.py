"""
Empty server that send the _bare_ minimum data to keep a minecraft client connected
"""
import logging
import random
from argparse import ArgumentParser

from quarry.types.buffer import Buffer

import config
from chunk import Chunk

from twisted.internet import reactor
from quarry.net.server import ServerFactory, ServerProtocol

from quarry.types.uuid import UUID

chunks = list()

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

        super(StoneWallProtocol, self).__init__(factory, remote_addr)

    def player_joined(self):
        super().player_joined()

        # Sent init packets
        self.send_packet("join_game",
                         self.buff_type.pack("iBqiB", 0, 3, 0, 0, 0),
                         self.buff_type.pack_string("flat"),
                         self.buff_type.pack_varint(6),
                         self.buff_type.pack("??", False, True))

        self.ticker.add_loop(20, self.send_keep_alive)  # Keep alive packets

        self.current_chunk = random.choice(chunks)

        self.send_chunk()

    def packet_animation(self, buff):
        buff.unpack_varint()
        self.next_viewpoint()

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

        # Credits
        self.send_packet('chat_message',
                         self.buff_type.pack_string( self.current_chunk.credit_json()),
                         self.buff_type.pack("b", 1))

    def send_viewpoint(self):
        viewpoint =  self.current_chunk.viewpoints[self.current_viewpoint]
        x = viewpoint.get('x')
        z = viewpoint.get('z')
        outside_chunk = x >= 16 or x < 0 or z > 0 or z <= -16

        # Player hasn't spawned yet and viewpoint is inside chunk
        # Spawn them outside to prevent movement
        if self.player_spawned is False and outside_chunk is False:
                self.send_packet("player_position_and_look",
                             self.buff_type.pack("dddff?", 16.0, 65, -16, 0.0, 0.0, 0b00000),
                                    self.buff_type.pack_varint(0))

                self.player_spawned = True

        # Viewpoint is outside chunk, unspectate viewpoint entity and teleport player
        # This also spawns the player if they aren't already
        if outside_chunk is True:
            if self.viewpoint_used is True:
                self.send_packet('camera', self.buff_type.pack_varint(0))
                self.viewpoint_used = False

            self.send_packet("player_position_and_look",
                             self.buff_type.pack("dddff?", x,
                                                 viewpoint.get('y'),
                                                 z,
                                                 viewpoint.get('yaw'),
                                                 viewpoint.get('pitch'),
                                                 0b00000),
                             self.buff_type.pack_varint(0))

            self.player_spawned = True

        # Viewpoint is inside chunk, teleport and spectate viewpoint entity
        else:
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

                #self.send_packet('entity_look', self.buff_type.pack_varint(self.viewpoint_id), self.buff_type.pack("bbB", viewpoint.get('yaw_256'), viewpoint.get('pitch'), 0))
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
        else:
            self.next_chunk()

    def next_chunk(self):
        if len(chunks) == 1:
            return

        current_chunk = self.current_chunk

        while current_chunk == self.current_chunk:
            self.current_chunk = random.choice(chunks)

        self.player_spawned = False
        self.viewpoint_spawned = False
        self.viewpoint_used = False
        self.raining = False

        self.send_packet("respawn", self.buff_type.pack("iBq", 1, 3, 0), self.buff_type.pack_string("flat"))
        self.send_packet("respawn", self.buff_type.pack("iBq", 0, 3, 0), self.buff_type.pack_string("flat"))
        self.send_chunk()
    def send_keep_alive(self):
        self.send_packet("keep_alive", self.buff_type.pack("Q", 0))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-a", "--host", default="127.0.0.1", help="bind address")
    parser.add_argument("-p", "--port", default=25567, type=int, help="bind port")
    parser.add_argument("-m", "--max", default=65535, type=int, help="player count")
    args = parser.parse_args()

    server_factory = ServerFactory()
    server_factory.protocol = StoneWallProtocol
    server_factory.max_players = args.max
    server_factory.motd = "Queue Server"
    server_factory.online_mode = False

    chunks = config.load_chunk_config()

    if len(chunks) is 0:
        logging.getLogger('main').error("No chunks defined. Exiting.")
        exit(1)

    server_factory.listen(args.host, args.port)
    reactor.run()

    logging.getLogger('main').info("Server started")
