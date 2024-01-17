SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/hdl/hbus_mem.v
#VERILOG_SOURCES += $(PWD)/wrappers/


dut:
	$(MAKE) sim MODULE= TOPLEVEL=
include $(shell cocotb-config --makefiles)/Makefile.sim
