import cocotb
from cocotb_bus.drivers import BusDriver
from cocotb.triggers import RisingEdge, FallingEdge, ReadOnly, Timer, ReadWrite, Lock

import random


class HyperbusMaster(BusDriver):
    _signals = ["cs", "rwds", "dq", "clk"]
    optional_signals = ["clk_"]

    def __init__(self, name, **kwargs):
        super().__init__(self, name, **kwargs)

    async def _driver_send(self, data):
        self.generate_clk()  # This should be in a start_soon block check https://docs.cocotb.org/en/stable/coroutines.html#concurrent-execution
        self.check_rwds_timing()
        self.bus.cs.value = 0
        await RisingEdge(self.bus.clk)
        # data transmission logic
        for bit in data:
            self.bus.dq.value = bit
            await RisingEdge(self.bus.clk)

        self.bus.cs.value = 1

    async def generate_clk(self):
        clk = HyperbusClock(self.bus.clk, 10, units="ns")
        await clk.start()

    async def check_rwds_timing(self):
        """Checks if RWDS is asserted before DQ on each clock cycle."""
        while True:
            await RisingEdge(self.bus.clk)
            assert self.bus.rwds.value == 1 and self.bus.dq.value == 0


@cocotb.coroutine
class HyperbusClock:  # JVS: Why define this class when https://docs.cocotb.org/en/stable/library_reference.html#clock exists?
    def __init__(self, signal, period, duty_cycle=60, units="ns"):
        self.signal = signal
        self.period = cocotb.utils.get_sim_steps(period, units)
        self.duty_cycle = duty_cycle
        self.high_time = int(self.period * duty_cycle / 100)
        self.low_time = self.period - self.high_time

    async def start(self):
        while True:
            self.signal <= 1
            await Timer(self.high_time, units="ns")
            self.signal <= 0
            await Timer(self.low_time, units="ns")

    async def write(self, address, data, burst: bool = False):
        """
        Writes a byte string of data to a specified Hyperbus address.
        Parameters:
        address: The target address on the Hyperbus.
        data: The byte string or bytearray containing the data to be written.
        Returns:
        TypeError: If the data is not of type bytes or bytearray.
        """
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be of type bytes or bytearray.")
        try:
            if burst:
                burst_length = self._calc_burst(data)
                # (0, 64, 64)->runs only once and offset->0
                for offset in range(0, len(data), burst_length):
                    # (address+0, data[0:64] ->single burst write
                    await self._perform_write(
                        address + offset, data[offset: offset + burst_length]
                    )
            else:
                await self._perform_write(address, data)
        except Exception as e:
            print(f"Error during write: {e}")

    async def _perform_write(self, address, data):
        try:
            self.bus.cs.value <= 0

            await self.transfer_ca_words(address, burst=False)

            await RisingEdge(self.bus.clk)
            await self._wait_for_ready()
        finally:
            self.bus.cs.value <= 1

    async def _wait_for_ready(self):
        await Timer(10, units="ns")

    def _calc_burst(self, data):  # considering 64-byte ->return 1
        burst_length_map = {
            128: None,  # 00 for infinite burst
            64: 1,  # 01 for 64 bytes
            16: 2,  # 10 for 16 bytes
            32: 3,  # 11 for 32 bytes
        }

        for length, code in burst_length_map.items():
            if len(data) % length == 0:
                return code
            else:
                return 1

    async def transfer_ca_words(self, address, burst):
        ca_words = []
        for ca_word in ca_words:
            for bit in ca_word:
                self.bus.dq.value = bit
                await RisingEdge(self.bus.clk)  # Synchronize with clock

    async def read(self, address, length):
        """
        Reads data from the specified Hyperbus address.
        Parameters:
            address: The target address to read from.
            length:  The number of bytes to read.
        Returns:
            The read data as a byte string.
        """
        try:
            self.bus.cs.value <= 0  # Assert CS
            # Set burst=False for read
            await self.transfer_ca_words(address, burst=False)

            # Receive data bytes
            read_data = bytearray()
            for _ in range(length):
                for i in range(8):
                    bit = self.bus.dq.value
                    read_data.append(bit)
                    await RisingEdge(self.bus.clk)

            await self._wait_for_ready()

        finally:
            self.bus.cs.value <= 1  # Deassert CS
            return read_data

    def rwds(self, is_read_transaction, read_data=None, write_mask=None):
        """
        Formats the Read-Write Data Strobe (RWDS) signal.

        Parameters:
            is_read_transaction: A boolean indicating whether it's a read transaction.
            read_data: The data payload associated with the read transaction.
            write_mask: The data payload associated with the write transaction.

        """
        if is_read_transaction:
            return read_data
        else:
            return write_mask


class AddressSpace(BusDriver):
    def __init__(self):
        self.address_space = {}

    def translate_logical_address(self, address):
        if not (
            self.get_constraints()["min_address"]
            <= address
            <= self.get_constraints()["max_address"]
        ):
            raise ValueError("Invalid address")

        # Basic example using a dictionary mapping
        if address in self.address_space:
            return self.address_space[address]
        else:
            raise ValueError("Address not found in address_space")

    def get_constraints(self):
        """
        Returns a dictionary containing constraints related to the address space.
        """
        constraints = {
            "min_address": 0,
            "max_address": 0xFFFF,
            "memory_base_address": 0x1000,
            "register_base_address": 0x0,
            "min_burst_length": 1,
            "max_burst_length": 128,
            "wrap_length": 1024,
        }
        return constraints


class HyperbusTransactionGenerator(BusDriver):
    def __init__(self):
        self.commands = ["READ", "WRITE"]
        self.min_burst_length = 1  # Set minimum burst length constraint
        self.max_burst_length = 128  # Set maximum burst length constraint

    def get_burst_length(self):
        """
        Generates a random burst length within constraints.
        """
        return random.randint(self.min_burst_length, self.max_burst_length)

    def generate_next_transaction(self):
        """
        Generates a random transaction with command, address, data, and burst length.
        """
        command = random.choice(self.commands)
        address = random.randint(0, self.wrap_length - 1)
        data_length = random.randint(1, 128)
        data = bytes([random.randint(0, 255) for _ in range(data_length)])
        burst_length = self.get_burst_length()
        transaction = {
            "command": command,
            "address": address,
            "data": data,
            "burst_length": burst_length,
        }
        if self.is_memory_access(address):
            transaction["target"] = "memory"
        else:
            transaction["target"] = "register"

        return transaction

    def _is_memory_access(self, address):
        """
        Determines if the given address is a memory access.
        """
        return address >= 0x1000
