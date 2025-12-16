import logging

from prometheus_client import start_http_server, Gauge

# Create a metric to track time spent and requests made.
players_online = Gauge('mc_players_online', 'Number of players connected to the server')


def init_prometheus(host, port):
    start_http_server(port, host)
    logging.getLogger(__name__).info(f'Prometheus client started on port {host}:{port}')


def set_players_online(count):
    players_online.set(count)
