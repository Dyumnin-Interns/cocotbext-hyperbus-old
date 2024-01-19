SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/hdl/hbus_mem.v
VERILOG_SOURCES += $(PWD)/hdl/hbus_cntrl.v
VERILOG_SOURCES += $(PWD)/wrapper/hbus_test.v

dut:
	$(MAKE) sim MODULE=h_test TOPLEVEL=hbus_test
include $(shell cocotb-config --makefiles)/Makefile.sim
