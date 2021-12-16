
from multiprocessing import Process
import pynvml as nvml
from enum import Enum
import time
import json
import signal

from p2pconnect import P2PServer
from delaymicrosecond import delayMicrosecond

class STATUS(Enum):
    INIT=0
    STOP=1
    WATCHING=2

class GPUMemWatch:
    def __init__(self, server, interval=100, devID = 0, outfile="watch.json"):
        self._interval = interval # 微秒
        self._devID = devID
        self._server = server # (ip, port)
        self.record = {}
        self._status = STATUS.INIT
        self._init = False
        self._outfile = outfile

    def nvmlInit(self):
        if self._init == False:
            nvml.nvmlInit()
            self._init = True

    def printGPUsInfo(self):
        self.nvmlInit()
        self._deviceNum = nvml.nvmlDeviceGetCount()
        print(f"\n\rGPU Device list:")
        for i in range(self._deviceNum):
            devHandle = nvml.nvmlDeviceGetHandleByIndex(i)
            devName = str(nvml.nvmlDeviceGetName(devHandle))
            print(f"\n\r\t{i}/{self._deviceNum}\t{devName}")

    def setDevice(self, devID):
        self._devHandle = nvml.nvmlDeviceGetHandleByIndex(devID)

    def getGPUMem(self):
        memSummary = nvml.nvmlDeviceGetMemoryInfo(self._devHandle)
        return memSummary.free, memSummary.used, memSummary.total

    def save(self):
        with open(self._outfile, "w") as f:
            json.dump(self.record, f, indent=2)
    
    def _sigint_handle(self):
        self._conn.close()
        self.save()
        exit(1)

    def watch(self, devID):
        self.nvmlInit()
        self.setDevice(devID)
        self._conn = P2PServer(self._server, block=False)
        self._conn.connectInit()
        self._status=STATUS.STOP
        signal.signal(signal.SIGINT, self._sigint_handle)
        while True:
            command = self._conn.recv()
            # do
            if command == "START":
                self._status = STATUS.WATCHING
            elif command == "STOP":
                self._status = STATUS.STOP
            elif command == "QUIT":
                break

            if self._status is STATUS.WATCHING:
                self.record[time.time()] = self.getGPUMem() # free, used, total
            delayMicrosecond(self._interval)

        self._conn.close()
        self.save()

def testClient():
    from p2pconnect import P2PClient
    import time
    client = P2PClient()
    client.connectInit()
    client.send("START")
    time.sleep(1)
    client.send("STOP")
    client.send("QUIT")

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("role", type=str, help="watcher/client")
    args = parser.parse_args()
    if args.role == "watcher":
        gpuwatch = GPUMemWatch(("127.0.0.1", 3344))
        gpuwatch.printGPUsInfo()
        gpuwatch.watch(0)
    elif args.role == "client":
        testClient()
    else:
        parser.print_help()