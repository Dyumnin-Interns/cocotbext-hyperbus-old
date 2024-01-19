import cocotb
from cocotb.result import TestFailure
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb.triggers import Timer
import os
from dut_init import dut_init 
from HyperbusMaster import HyperbusMaster
from HyperbusSlave import HyperbusSlave
#from dut_monitor import Wishbone
import random

@CoverPoint("hyperbus_master.bus.cs", bins=[0, 1])
def cs_cover(cs):
    pass

@CoverPoint("hyperbus_master.bus.dq", bins=range(256))
def dq_cover(dq):
    pass

@CoverPoint("hyperbus_master.bus.rwds", bins=[0, 1])
def rwds_cover(rwds):
    pass

@cocotb.test()
async def test_dut(dut):
    await dut_init(dut)
    hyperbus_master = HyperbusMaster(dut, "hyperbus_master", dut.CLK)
    hyperbus_slave = HyperbusSlave(dut, "hyperbus_slave", dut.CLK)
    
    global expected_value
    expected_value = []

    # Configuration parameters
    latency = 10
    burst_length = 64
    burst_increment = 4

    # Apply initial latency
    await hyperbus_master._wait_for_ready(latency)

    # Test 
    address = 0x1000
    data = b'This is a data string I am sending over hyperbus;'
    await hyperbus_slave.write(address, data, burst=True, burst_length=burst_length, burst_increment=burst_increment)
    expected_value.append(sum(data))

    await Timer(1, "ns")
   
   # Perform read operation
    read_data = await hyperbus_master.read(address, len(data))
    print(f"Read Data: {read_data}")

  # hyperbus operations
    await hyperbus_master.initialize()  # for verification
    await hyperbus_master.write_data(0x1000, 0xabcdabcd, reg=False)  # write data 0xabcdabcd to address 0x1000
    read_data = await hyperbus_master.read(0x1000, len(data), reg=False)  # read data from address 0x1000

    coverage_db.report_coverage(cocotb.log.info, bins=True)
    coverage_file = os.path.join(os.getenv("RESULT_PATH", "./"), "coverage.xml")
    coverage_db.export_to_xml(filename=coverage_file)
