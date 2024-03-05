set_property SRC_FILE_INFO {cfile:/home/galrene/school/bakalarka/RDS/basys3/rene_test/rene_test.srcs/constrs_1/imports/xdc/constraints_RDS.xdc rfile:../../../rene_test.srcs/constrs_1/imports/xdc/constraints_RDS.xdc id:1} [current_design]
set_property src_info {type:XDC file:1 line:7 export:INPUT save:INPUT read:READ} [current_design]
set_property PACKAGE_PIN W5 [get_ports clk_in]
set_property src_info {type:XDC file:1 line:10 export:INPUT save:INPUT read:READ} [current_design]
set_property PACKAGE_PIN R2 [get_ports reset_n_in]
set_property src_info {type:XDC file:1 line:13 export:INPUT save:INPUT read:READ} [current_design]
create_pblock pblock_AES
add_cells_to_pblock [get_pblocks pblock_AES] [get_cells -quiet [list aes]]
resize_pblock [get_pblocks pblock_AES] -add {SLICE_X0Y100:SLICE_X9Y149}
set_property EXCLUDE_PLACEMENT 1 [get_pblocks pblock_AES]
set_property src_info {type:XDC file:1 line:19 export:INPUT save:INPUT read:READ} [current_design]
create_pblock pblock_REGISTERS
add_cells_to_pblock [get_pblocks pblock_REGISTERS] [get_cells {sensor/tdc0/sensor_o_regs[*].obs_regs}]
resize_pblock [get_pblocks pblock_REGISTERS] -add {SLICE_X12Y100:SLICE_X17Y104}
set_property EXCLUDE_PLACEMENT 1 [get_pblocks pblock_REGISTERS]
set_property src_info {type:XDC file:1 line:24 export:INPUT save:INPUT read:READ} [current_design]
create_pblock pblock_SENSOR
add_cells_to_pblock [get_pblocks pblock_SENSOR] [get_cells {sensor/tdc0/coarse_init sensor/tdc0/coarse_ld_init sensor/tdc0/fine_init {sensor/tdc0/fine_chain_carry[*].fine_carry} {sensor/tdc0/pre_buf_chain_gen[*].ld_chain} {sensor/tdc0/pre_buf_chain_gen[*].lut_chain}}]
resize_pblock [get_pblocks pblock_SENSOR] -add {SLICE_X10Y100:SLICE_X11Y149}
set_property EXCLUDE_PLACEMENT 1 [get_pblocks pblock_SENSOR]
set_property src_info {type:XDC file:1 line:32 export:INPUT save:INPUT read:READ} [current_design]
create_pblock pblock_BOTTOM
add_cells_to_pblock [get_pblocks pblock_BOTTOM] [get_cells *delay*]
add_cells_to_pblock [get_pblocks pblock_BOTTOM] [get_cells {io_controller reset_system}]
resize_pblock [get_pblocks pblock_BOTTOM] -add {CLOCKREGION_X0Y0:CLOCKREGION_X1Y0}
set_property src_info {type:XDC file:1 line:33 export:INPUT save:INPUT read:READ} [current_design]
add_cells_to_pblock [get_pblocks pblock_BOTTOM] [get_cells -quiet [list ttest]]
set_property src_info {type:XDC file:1 line:38 export:INPUT save:INPUT read:READ} [current_design]
add_cells_to_pblock [get_pblocks pblock_BOTTOM] [get_cells *ttest*]
set_property src_info {type:XDC file:1 line:40 export:INPUT save:INPUT read:READ} [current_design]
set_property PACKAGE_PIN B18 [get_ports rx_i]
set_property src_info {type:XDC file:1 line:42 export:INPUT save:INPUT read:READ} [current_design]
set_property PACKAGE_PIN A18 [get_ports tx_o]
