import cocotb
from cocotb_bus.drivers import BusDriver
from cocotb.triggers import RisingEdge, FallingEdge, ReadOnly, Timer, ReadWrite, Lock


class HyperbusSlave(BusDriver):
    _signals = ["cs", "rwds", "dq", "clk", "memory"]
    optional_signals = ["clk_"]

    def __init__(self, name, memory_size, hb_ca, **kwargs):
        super().__init__(self, name, **kwargs)
        self.memory_model = {}
        for i in range(memory_size):
            self.memory_model[i] = 0  # initialize all bytes to 0
        self.hb_ca - hb_ca
        self.rwds_mask = 0xFF

    async def driver_send(self, data):
        await RisingEdge(self.bus.clk)
        self.bus.dq.value = data

    async def write(self, address, data):
        """
          Writes data to the slave memory based on address, considering burst transfers.
        Parameters:
        address: The target address to write to.
        data: The data to be written as a byte string.
        """
        burst_length = self._calc_burst(data)
        for i in range(burst_length):
            self.memory_model[address + i] = data[i]

    async def read(self, address, length):
        """
         Reads data from the slave memory based on address
        Parameters:
        address: The target address to read from.
        length: The number of bytes to read.
        """
        read_data = bytearray(length)
        for i in range(length):
            if address + i in self.memory_model:
                read_data[i] = self.memory_model[address + i]
            else:
                read_data[i] = 0
            read_data[i] &= self.rwds_mask

            self.bus.dq.value = read_data[i]
        return read_data

    def _calc_burst(self, data):
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

    async def handle_transaction(self):
        await RisingEdge(self.bus.clk)

        if self.bus.cs.value == 0:
            try:
                # Access CA values with synchronization
                await RisingEdge(self.bus.clk)
                command, address, latency = await self.decode_command()
                length = 4  # Example value
                # Handle latency
                await self.process_latency(latency)

                if command == "write":
                    await self.write(address, data)
                elif command == "read":
                    data = await self.read(address, length)
                else:
                    raise ValueError(f"Unsupported command: {command}")

            except Exception as e:
                print(f"Error during transaction: {e}")

            finally:
                # Deassert CS with synchronization
                await RisingEdge(self.bus.clk)
                self.bus.cs.value = 1

    async def decode_command(self):
        """
        using the ca bit assignment logic for(read/write/address space/burst type/latency)
        """
        command = self.hb_ca[0].value
        address = (self.hb_ca[1].value << 8) | self.hb_ca[2].value
        latency = self.hb_ca[3].value
        return command, address, latency

    async def process_latency(self, latency):
        for _ in range(latency):
            await RisingEdge(self.bus.clk)
