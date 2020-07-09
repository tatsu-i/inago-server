import time
from multiprocessing import Process
from inago.driver import BinanceDriver

def main():
    process_list = []
    binance_driver = BinanceDriver(sym="BTCUSDT")
    process_list.append(Process(target=binance_driver.run))
    for p in process_list:
        p.start()

    while True:
        time.sleep(5)

if __name__ == "__main__":
    main()
