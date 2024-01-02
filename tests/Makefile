SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/hdl/
VERILOG_SOURCES += $(PWD)/wrappers/

dut:
	$(MAKE) sim MODULE= TOPLEVEL=
include $(shell cocotb-config --makefiles)/Makefile.sim