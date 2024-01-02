module hyperbusslave(
    input wire clk,
    input wire rst_n,
    output reg cs,
    inout wire dq,
    output reg rwds,
    input wire [31:0] address,
    input wire [31:0] data_in,
    output reg [31:0] data_out
);

 reg [31:0] memory [0:MEMORY_SIZE-1];

assign data_out = memory[read_address];  // Example for read operation
always @(posedge clk) begin
    if (write_enable) begin
        memory[write_address] = data_in;  // Example for write operation
    end
end

always @(posedge clk) begin
        if (!rst_n) begin
            cs <= 1;
            rwds <= 0;
        end 
        
    end


endmodule
