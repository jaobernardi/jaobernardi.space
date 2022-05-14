from lib.structures import HTTPServer, Response
from lib import config, utils

utils.load_handlers()

server = HTTPServer(**config.get_web())
server.spin_up()
