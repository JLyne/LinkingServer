import logging

from prometheus_client import start_http_server, Summary, Counter, Gauge

# Create a metric to track time spent and requests made.
players_online = Gauge('mc_players_online_total', 'Number of players connected to the server')

def init_prometheus(port):
    start_http_server(port)
    print('Prometheus client started on port {}'.format(port))

def set_players_online(count):
    players_online.set(count)