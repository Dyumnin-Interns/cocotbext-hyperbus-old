
# Hyperbus interface modules for Cocotb

GitHub repository: https://github.com/Dyumnin-Interns/cocotbext-hyperbus




## Introduction

`HyperbusMaster` and `HyperbusSlave` are the two models for the protocol.




## Installation

Installation from pip (release version, stable):

    $ pip install cocotbext-hyperbus
    
Installation from git (latest development version, potentially unstable):

    $ pip install https://github.com/Dyumnin-Interns/cocotbext-hyperbus/archive/master.zip

Installation for active development:

    $ git clone https://github.com/Dyumnin-Interns/cocotbext-hyperbus
    $ pip install -e cocotbext-hyperbus

    
## Documentation
`HyperBusMaster`, `HyperBusAddressMap`, `HyperBusTransactionGenerator` classes implement HyperBus master model.
### HyperBusMaster Model
A HyperBus master plays a crucial role in initiating and managing data transfers on the HyperBus. It acts as   the brain of the HyperBus communication, managing the exchange of data between itself and HyperBus slaves (e.g., HyperFlash memory)

This model represents the following functionalities:
* Generate HyperBus commands (read, write, burst)
* Translate logical addresses to physical addresses
* Transfer data over the HyperBus bus
* Handle errors and report them

To use the module, import the classes:

```bash
from cocotbrxt.hyperbus import HyperbusMaster,  HyperBusTransactionGenerator
from cocotbext.axi import AdressSpace

signals=cs, rwdq dq,clk clk#

cfg=HyperbusCfg(burst=False)
cfg.burst=False
hmas=HyperbusMaster(dut,prefix="hy1",config=cfg)
cfg.burst=True
cfg.burstlength=random.choice(1,23,3)
hmas.configure(cfg)

address = 0x1000
data=b'This is a data string I am sending over hyperbus;'
data=[0x00, 0x100,0xfa99]
data=readmem(memfile)
hmas.write(address,data,burst=False,reg=True)
irdata=hmas.read(address,length=len(data),burst=False,reg=True)
assert irdata=data,"datamismatch"
cover(burstlen)

someClass=SomeClass()
slv=HyperbusSlave(dut,prefix,target=someClass)


master_model = HyperbusMaster(clk, hb_cmd, hb_addr, hb_wr_data, hb_rd_data, hb_rw, hb_cs, hb_ca)
```

#### Signals:
* onWrite/Read
	* `hb_cmd` -hyberbus command signal used to indicate type of burst transaction: Burst_read or Burst_write
	* `hb_rw`   -sets to 1 to indicate a read operation
	* `hb_rw`- sets to 0 to indicate a write operation
	* `hb_wr_data` - sets the value of the data to be written
	* `hb_rd_data` -reads data value and stores in the data variable
	* `write_data` - waits for rising edge on  clock to confirm write completion
	* `read_data` -waits for rising edge on clock to receive the read data
	* `hb_addr` -sets to the desired address
* Not exposed to user
	* `hb_cs`    -sets to the value 0 to activate the selected slave device
	* `hb_cs`    -sets value back to 1 to deactivate the slave device
* As CFG class
	* `latency` -Initial latency value to be applied before every transaction.
	* `Burst_length` -specifies the total number of transfers in the burst transaction.
	* `Burst_increment` -specifies the amount by which the address is incremented after each transfer in the burst

`read_data` and `write_data` perform read and write operations on the hyperbusmaster.
```bash
await master_model.initialize() #for verification
     #read and write transactions
     read_data = await master_model.read(0x1000,length,reg=False)  #read data from address 0x1000
     await master_model.write_data(0x1000, 0xabcdabcd,reg=False)  #write data 0xabcdabcd to address 0x1000
```
#### HyperBusAddressMap Reuse from axi
This class manages the mapping between logical and physical addresses used by the HyperBus master.
```bash
class HyperbusAddressMap:
#define mapping between logical and physical address       
def _init_():
        address_map = { }
        def translate_logical_address(address):
        return address_map[address]   #convert logical address to physical address
```

#### Additional Signals:
* read_data: Reads data from a specific address on the HyperBus.
* write_data: Writes data to a specific address on the HyperBus.
* burst_transfer: Performs a burst transfer of data on the HyperBus.
* wait_for_ack: Waits for an acknowledgment signal from the slave device.
* handle_error: Handles errors detected during transactions.


#### Command/Address(CA) bit assignments:

Bit 47 - R/W# – 0-write
                1-read

Bit 46 - Target addr space – 0-memory space
                             1-register space

Bit 45 - Burst type –0-wrapped
                     1-Linear

Bit 44-16 - Address(half-page sector) – (A31-A3)->29 bits: Row and upper column address

Bit 15-3 - Reserved –Dont care(Set to 0)

Bit 2-0 -Address(word within half-page) – (A2-A0) 16 bytes

#### READ Transactions:
* HyperBusMaster drives CS# low while clock is idle.
* Clock starts toggling while CommandAddress (CA) words are transferred.
* CA0 indicates read transaction-CA[47] = 1, memory space-CA[46] = 0, and burst type- CA[45].

Burst types-
 Wrapped bursts wrap within the burst length whereas linear bursts output data sequentially across row boundaries.
* CA1 and CA2 provide row/column address and target word address.
* Master starts driving CS# low only after satisfying Read-Write-Recovery time (tRWR).

Latency:
* Master clocks for a number of cycles defined by the latency count setting.
* RWDS signal determines additional latency based on its value during CA cycles.

Data Transfer:
* RWDS transitions and data output occur simultaneously after latency cycles.
* New data is output edge-aligned with every RWDS transition.
* RWDS may go low between words for latency insertion or error indication.

Termination:
* Read transfer ends by driving CS# high when the clock is idle.
* Clock can be idle while CS# is high.


#### WRITE Transactions:
* Master drives CS# low while clock is idle.
* Clock starts toggling while Command-Address (CA) words are transferred.
* CA0 indicates CA[47]=0-write transaction and CA[46]=0-memory space CA[45]-Burst type
* CA1 and CA2 provide row/column address and target word address.
* Master starts driving CS# low only after satisfying Read-Write-Recovery time (tRWR).

Latency:
* Master clocks for a number of cycles defined by the latency count setting.
* RWDS signal during CA cycles may determine additional latency (device dependent).

Data Transfer:
* Master starts outputting write data after latency cycles.
* Write data is center-aligned with clock edges (first byte captured on rising edge, second on falling edge).
* RWDS is driven by the master during data transfer as a data mask.
* Data is written to the array only when RWDS is Low.
* Master cannot indicate a need for latency within the write data transfer portion.
* Slave must be able to accept a continuous burst of write data or have a limit on the acceptable burst length (device dependent).

Termination:
* Write transfer ends by driving CS# high when the clock is idle.
* Some devices may not support wrapped write transactions.
* Linear burst writes may have device-dependent behavior when reaching the last address.

#### Write transaction without initial latency:
* No turnaround period for RWDS eliminates initial latency, potentially improving write transaction speed.
* Simplified communication: Slave only needs to drive RWDS during the Command-Address period, reducing communication overhead.
* Master restrictions: Master must not drive RWDS during zero latency writes and treat all data as full word writes.
* Device dependence: Requirement for zero latency writes and its use for memory/register space vary depending on the slave device.
* Configuration setting: Master interface needs a configuration option to enable zero latency writes for specific address spaces.
* Continuous data transfer: Slave must accept a continuous burst of write data or the master must limit the burst length.


### HyperBusSlave Model
The HyperBus slave model is responsible for responding to commands and facilitating data exchange on the bus. It plays a critical role in ensuring accurate and efficient communication within the system.

Functionalities of the model include:
* Receive HyperBus commands and data
* Respond to read and write requests
* Handle address decoding and data storage
* Report errors to the master

To use the module, import the class:
```bash
from hyperbus_model import HyperbusSlave

slave_model=HyperbusSlave(clk, hb_cs, hb_ca, hb_rw, hb_rd_data, hb_wr_data, memory)
```

The HyperbusSlave model defines a asyn function `handle_transaction` that waits for the rising edge on clock,
-CS is asserted low, indicating transaction start.
```bash
async def handle_transaction():
    await RisingEdge(clk)
       If cs.value != 0:  #chip select assertion check
         break
```

A `decode_command` is defined to decode the CA words-command type(read/write), address space(memory/register),burst type(wrapped/linear),latency count.
```bash
def decode_command():
    command = hb_ca[0].value #using the ca bit assignment logic for(read/write/address space/burst type/latency)
    address = hb_ca[1].value << 8 | hb_ca[2].value
    latency = hb_ca[3].value
```

The `process_latency` function uses latency information from CA words and waits for the required number of clock cycles based on latency.
```bash
async def process_latency(latency):
   for _in range(latency)
        await RisingEdge(clk)
```

`read_data` and `write_data` functions receives address as input.
`read_data` checks if the address exits in the memory dictionary. If exists:

-read data from memory location.

-apply RDWS mask to write data

-send data to output signals

-if address is invalid, set all data outputs to 0 to indicate an error.

`write_data` writes data to memory location based on address, considering burst transfers.


#### Signal Parameters:
Master Outputs, Slave Inputs:
* `CS#`: Chip Select- Initiates and terminates bus transactions. High to Low activates, Low to High deactivates.
* `CK, CK#`:    Differential clock signals for data transfer synchronization.
* `DQ[7:0]`:      Data input/output for command, address, and data information.
* `RWDS`:       Read/Write data strobe, indicates additional latency or data mask.
* `RESET#`:    Resets DQ signals to High-Z state when Low.

Slave Outputs, Master Inputs:
* `RSTO#` (Open Drain):   Indicates Power-On-Reset (POR) in the slave device.
* `INT#` (Open Drain):       Indicates an internal event in the slave device.
