module hyperbusmaster(
    input wire clk,
    input wire rst_n,
    output reg cs,
    inout wire dq,
    output reg rwds,
    input wire [31:0] address,
    input wire [31:0] data_in,
    output reg [31:0] data_out
);

always @(posedge clk) begin
        if (!rst_n) begin
            cs <= 1;
            rwds <= 0;
        end 
        
    end



endmodule
