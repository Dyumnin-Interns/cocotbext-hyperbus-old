import cocotb
from cocotb_bus.drivers import BusDriver
from cocotb.triggers import RisingEdge, FallingEdge, ReadOnly, Timer, ReadWrite, Lock

class HyperbusMaster(BusDriver):
    _signals=[...]
    _optional_signals=[...]
    def __init__(self,...):
        pass
    def write(self,address,data):
        '''
        Description of what the function does.
        description of each parameter.
        '''
        pass
    def _calc_burst(data):
        burst_length = data // 32
        return burst_length if burst_length > 0 else 1

class HyperbusAddressMap(BusDriver):
    def _init_(self):
        pass
        '''
        define mapping between logical and physical address     
        '''

class HyperbusTransactionGenerator(BusDriver):
    def 

