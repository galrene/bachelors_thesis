// Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2018.3 (lin64) Build 2405991 Thu Dec  6 23:36:41 MST 2018
// Date        : Wed Feb 28 15:58:05 2024
// Host        : RENENTB running 64-bit Ubuntu 23.10
// Command     : write_verilog -force -mode synth_stub
//               /home/galrene/school/bakalarka/RDS/basys3/rene_test/rene_test.srcs/sources_1/ip/clock_generator/clock_generator_stub.v
// Design      : clock_generator
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7a35tcpg236-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
module clock_generator(aes_clk, sensor_clk, ttest_clk, resetn, locked, 
  clk_in1)
/* synthesis syn_black_box black_box_pad_pin="aes_clk,sensor_clk,ttest_clk,resetn,locked,clk_in1" */;
  output aes_clk;
  output sensor_clk;
  output ttest_clk;
  input resetn;
  output locked;
  input clk_in1;
endmodule
