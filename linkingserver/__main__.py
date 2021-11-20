import os
import sys
from argparse import ArgumentParser

from quarry.net.server import ServerFactory
from twisted.internet import reactor

from linkingserver.config import load_config
from linkingserver.log import logger
from linkingserver.prometheus import init_prometheus
from linkingserver.protocol import Protocol, build_versions

if getattr(sys, 'frozen', False):  # PyInstaller adds this attribute
    # Running in a bundle
    path = os.path.join(sys._MEIPASS, 'linkingserver')
else:
    # Running in normal Python environment
    path = os.path.dirname(__file__)

parser = ArgumentParser()
parser.add_argument("-a", "--host", default="127.0.0.1", help="bind address")
parser.add_argument("-p", "--port", default=25567, type=int, help="bind port")
parser.add_argument("-m", "--max", default=65535, type=int, help="player count")
parser.add_argument("-r", "--metrics", default=None, type=int, help="expose prometheus metrics on specified port")

args = parser.parse_args()

server_factory = ServerFactory()
server_factory.protocol = Protocol
server_factory.max_players = args.max
server_factory.motd = "Linking Server"
server_factory.online_mode = False
server_factory.compression_threshold = 5646848

metrics_port = args.metrics

if metrics_port is not None:
    init_prometheus(metrics_port)

config = load_config()
Protocol.linking_secret = config['secret']

build_versions()

server_factory.listen(args.host, args.port)
logger.info('Server started')
logger.info("Listening on {}:{}".format(args.host, args.port))
reactor.run()
