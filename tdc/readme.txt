Commissioning the Time to Digital Converter
---------------------
---------------------


The TDC wrapper is the interface between the TDC and the higher-level logic. This is where 
signals required for operation are generated and the cross-clock interface is instantiated.
interface is instantiated.

----------------------
-- Interface:
----------------------
clk: Clock of the higher-level logic
ce: No function
CLK_PIN: Signal of the clock pin of the FPGA
RST: High Active Reset. The TDC _must_ be reset after the system start.

START: Start signal of the time measurement
STOP: Stop signal of the time measurement
CALIB_EN: TDC is calibrated as long as CALIB_EN = '1'.
READY: Signals to the higher-level logic that the initial calibration has been carried out after the reset.
        reset has been performed. If READY = '1', time measurements can be carried out.

time_fifo_*:    Read side of the FWFT-FIFO for transmitting the TDC measured values across the clock limit.
                across the clock limit.
period_fifo_*:  Write side of the FIFO, which is used to adjust the time value of a clock cycle used to calculate the measurement result.
                measurement result in picoseconds CLK_IN_PS.


----------------------
-- Constraints:
----------------------

The elements of the TDL sections of the TDC are automatically placed relative to each other by constraints in the code.
automatically by constraints in the code. However, the placement of the individual sections must be carried out manually.
be carried out manually.

The TDC is placed in the same clock region in which the I/O pins of the clock signal are located.
are located. The TDC sections are placed in the upper half of the clock region as parallel to each other as possible.
placed next to each other. If you place the sections of the 0 and 180 degree phase of a TSP
are placed together in a column of CLBs, they can use the same clock line.

The data processing of the TDC takes place in the same clock region.

Using the PBLOCK constraint, the ring oscillator, which generates the calibration signal
signal can be narrowed down to one area in Vivado in the vicinity of the global clock buffers in order to
achieve an oscillation frequency that is as constant as possible over several implementation runs.
over several implementation runs.


----------------------
-- Adjustments:
----------------------

If the start and stop signals are to be routed internally on the FPGA for test purposes, the BUFRs
in the TDC module, which route the start and stop signals to the multiplexers that switch between clock
and calibration signals must be commented out and replaced by a direct signal assignment.
by a direct signal assignment.

A structure for externalising the values of the calibration histogram is commented out in the code.
If you want to use this functionality, the dbg_* signals in the code of the tdc_pkg, LUT, Channel,
TDC and TDC_Wrapper modules. If dbg_down.hist_en is set, the next complete histogram is displayed with the
histogram is routed outwards with the dbg_up line.
The dbg_* structure can be extended for any other purpose.