import cocotb
from cocotb_bus.drivers import BusDriver
from cocotb.triggers import RisingEdge, FallingEdge, ReadOnly, Timer, ReadWrite, Lock
import random

class HyperbusMaster(BusDriver):
    _signals=['cs', 'rwds', 'dq', 'clk']
    _optional_signals=['clk_']
    def __init__(self, cs, rwds, dq, clk):
        self.bus.cs=cs
        self.bus.rwds=rwds
        self.bus.dq=dq
        self.bus.clk=clk
       
       
       
    async def driver_send(self, data):
        
        #start clock generation and checker tasks
        self.generate_clk()  
        self.check_rwds_timing()  

        self.bus.cs.value = 0

        
        await self.tosv.is_high  # Ensure slave is ready

        for bit in data:
           self.bus.rwds.value == 0
           self.bus.dq.value == bit
           await RisingEdge(self.clk)  # Synchronize with clock
           

    async def generate_clk(self):
        '''Toggles the DQ signal on each clock cycle.'''
        while True:
            await RisingEdge(self.bus.clk)
            self.bus.dq.value = not self.dut.dq.value

    async def check_rwds_timing(self):
        '''Checks if RWDS is asserted before DQ on each clock cycle.'''
        while True:
            await RisingEdge(self.bus.clk)
            assert self.bus.rwds.value == 1 before self.bus.dq.value == 1
        
       
    def write(self,address,data, burst=False):
      '''
  Writes a byte string of data to a specified Hyperbus address.

  Parameters:
    address: The target address on the Hyperbus.
    data: The byte string or bytearray containing the data to be written. 
  Rrturns:
    TypeError: If the data is not of type bytes or bytearray.
   
  '''
        if not isinstance(data, (bytes, bytearray)):
          raise TypeError("Data must be of type bytes or bytearray.")

      try:
        if burst:
            burst_length = self._calc_burst(data)  # Use correct burst length calculation
            for offset in range(burst_length):
                await self._perform_write(address + offset, data[offset::burst_length])
        else:
            await self._perform_write(address, data)
        
      except Exception as e:
            print(f"Error during write: {e}")
        
       
        
        
     aasync def _perform_write(self, address, data):
        try:
            self.bus.cs <= 0
            self.bus.address <= address
            for byte in data:
                self.bus.data <= byte
            await RisingEdge(self.bus.clk)
            await self._wait_for_ready()
        finally:
            self.bus.cs <= 1

    async def _wait_for_ready(self):
        # Placeholder for waiting until the slave is ready
        await Timer(10, units='ns')
    
    
    def _calc_burst(self, data):
           burst_length_map = {
            128: None,  # 00 for infinite burst
            64: 1,     # 01 for 64 bytes
            16: 2,     # 10 for 16 bytes
            32: 3,     # 11 for 32 bytes
        }

        for length, code in burst_length_map.items():
            if len(data) % length == 0:
                return code
            else 
                return 1

        
        
    def read(self, address, length):
        '''
        Reads data from the specified Hyperbus address.
    Parameters:
            address: The target address to read from.
            length:  The number of bytes to read.
    Returns:
            The read data as a byte string.
         '''
        
         expected_data = b'\x01\x02\x03'  # Replace with your expected data
         if read_data != expected_data:
            raise Exception(f"Data mismatch")

         return read_data
    

    def rwds(self, is_read_transaction, read_data=None, write_mask=None):
        '''
        Formats the Read-Write Data Strobe (RWDS) signal.

        Parameters:
            is_read_transaction: A boolean indicating whether it's a read transaction.
            read_data: The data payload associated with the read transaction.
            write_mask: The data payload associated with the write transaction.

        '''
        if is_read_transaction:
            
            return read_data
        else:
            return write_mask
        
 
class AddressSpace(BusDriver):
    def _init_(self): 
       self.address_space = { }
   def translate_logical_address(self, address):
        # Implement address translation logic here
        return physical_address
   
   def get_constraints(self):
        '''
        Returns a dictionary containing constraints related to the address space.
        '''
        constraints = {
            "min_address": 0,  # Adjust as needed
            "max_address": 0xFFFF,  # Adjust as needed
            "memory_base_address": 0x1000,  # Example memory base address
            "register_base_address": 0x0,  # Example register base address
            "min_burst_length": 1,
            "max_burst_length": 128,
            "wrap_length": 1024,
            
        }
        return constraints
        

class HyperbusTransactionGenerator(BusDriver):
    def __init__(self):
        self.commands = [READ, WRITE]
        self.min_burst_length = 1  # Set minimum burst length constraint
        self.max_burst_length = 128  # Set maximum burst length constraint

    def get_burst_length(self):
       '''
        Generates a random burst length within constraints.
        '''
        return random.randint(self.min_burst_length, self.max_burst_length)

    def generate_next_transaction(self):
       '''
        Generates a random transaction with command, address, data, and burst length.
        '''
        command = random.choice(self.commands)
        address = random.randint(0, self.wrap_length - 1)  # Address within wrap length
        data_length = random.randint(1, 128)  # Random number of bytes (adjust as needed)
        data = bytes([random.randint(0, 255) for _ in range(data_length)])
        

        transaction = {
            "command": command,
            "address": address,
            "data": data,
            "burst_length": burst_length
        }

        
        if self.is_memory_access(address):
            transaction["target"] = "memory"
        else:
            transaction["target"] = "register"

        return transaction

    def _is_memory_access(self, address):
       '''
        Determines if the given address is a memory access.
        '''
        return address >= 0x1000  
 
 
 
 
        
  
