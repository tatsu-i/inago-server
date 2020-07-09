from binance.client import Client
from binance.websockets import BinanceSocketManager
from .utils import epoch_to_datetime, mid_price, publish

class BinanceDriver:
    def __init__(self, sym="BTCUSDT"):
        self.sym = sym
        client = Client()
        self.bm = BinanceSocketManager(client)

    def process_message(self, msg):
        message = {"n": f"binance_{self.sym.lower()}", "t": msg["E"]/1000.0, "p": mid_price(msg["a"], msg["b"]), "a": msg["A"], "b": msg["B"]}
        publish(message, "raw")

    def run(self):
        self.bm.start_symbol_ticker_socket(self.sym, self.process_message)
        self.bm.start()
