module hbus_test (
         input wire cs,
         input wire clk,
         inout wire dq,
         output wire rwds

);

hbus dut(
    .cs(cs),
	.clk(clk),
    .dq(dq),
    .rwds(rwds)
	
);

initial begin
	$dumpfile("hbustest.vcd");
	$dumpvars;
end

endmodule
