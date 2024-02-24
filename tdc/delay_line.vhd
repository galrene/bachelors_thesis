-- TAPPED DELAY LINE
-- Instantiates the TDL. The phase is chosen according to PHASE.

library ieee;
use ieee.std_logic_1164.all;
use ieee.math_real.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.all;

library work;
use work.tdc_pkg.all;


entity DELAY_LINE is
    generic(
        PHASE   : STRING;
        CH      : STRING
    );
    port (
        CLK     : in STD_LOGIC;
        CLK_P90 : in STD_LOGIC;
        D       : in r_dl_in;
        Q       : out r_dl_out
    );
end entity;




architecture DELAY_LINE_ARCH of DELAY_LINE is

    attribute RLOC          : STRING;
    attribute DONT_TOUCH    : STRING;

    type r is record
        bins_sync           : STD_LOGIC_VECTOR(DEPTH*4-1 downto 0);
    end record;

    signal BINS             : STD_LOGIC_VECTOR(DEPTH*4-1 downto 0);
    signal CO0              : STD_LOGIC_VECTOR(3 downto 0);
    signal SENSOR_REG       : STD_LOGIC;

    signal S                : r;

    signal CLK_POL          : STD_LOGIC;
    signal CLK_SIM          : STD_LOGIC := '0';
begin

    -- Select sampling rate
    pol_0: if PHASE = "0" generate
        CLK_POL <= CLK;
    end generate;

    pol_90: if PHASE = "90" generate
        CLK_POL <= CLK_P90;
    end generate;

    pol_180: if PHASE = "180" generate
        CLK_POL <= not CLK;
    end generate;

    pol_270: if PHASE = "270" generate
        CLK_POL <= not CLK_P90;
    end generate;

    -- Output data
    q.BINS <= S.bins_sync;

    --------------------------------------------------------
    -- TODO: Instead of the first carry element there will be an initial delay line here!
    --------------------------------------------------------
    -- First carry element. Will not be sampled
    carry_0: if (not SIM) generate
        attribute RLOC of CARRY4_INST : label is "X0Y0";
        attribute RLOC of FDCE_INST   : label is "X0Y0";
    begin
        CARRY4_INST: CARRY4 port map (
            O       => open,        -- Carry chain XOR general data out => not used
            CO      => CO0,         -- Carry-out of each stage of the carry chain
            DI      => "0000",      -- Carry-MUX data input
            S       => "1111",      -- Carry-MUX select line
            CYINIT  => SENSOR_REG,  -- Carry-in initialization input
            CI      => '0'          -- Carry cascade input
        );

        -- D Flip-Flop with Clock Enable and Asynchronous Clear
        FDCE_INST: FDCE generic map (
            INIT => '0'
        ) port map (
            D   => '1',
            C   => d.sensor,
            CE  => '1',
            CLR => BINS(DEPTH*4-1),
            Q   => SENSOR_REG
        );
    end generate;

    -- CARRY CHAIN
    carry_logic: for i in 0 to DEPTH-1 generate
        -- Placement relative to carry_0.CARRY4_INST
        attribute RLOC of dff0 : label is "X0Y"&integer'image(i+1);
        attribute RLOC of dff1 : label is "X0Y"&integer'image(i+1);
        attribute RLOC of dff2 : label is "X0Y"&integer'image(i+1);
        attribute RLOC of dff3 : label is "X0Y"&integer'image(i+1);
    begin
        carry_1: if i = 0 and (not SIM) generate
            attribute DONT_TOUCH of CARRY4_INST : label is "True";
        begin
            CARRY4_INST: CARRY4 port map (
                O       => open,
                CO      => BINS(4*(i+1)-1 downto 4*i),
                DI      => "0000",
                S       => "1111",
                CYINIT  => '0',
                CI      => CO0(3)
            );
        end generate;

        carry_n: if i > 0 and (not SIM) generate
            attribute DONT_TOUCH of CARRY4_INST : label is "True";
        begin
            CARRY4_INST: CARRY4 port map (
                O       => open,
                CO      => BINS(4*(i+1)-1 downto 4*i),
                DI      => "0000",
                S       => "1111",
                CYINIT  => '0',
                CI      => BINS(4*i-1)
            );
        end generate;

        -- -- Simulates TDL (Tapped Delay Line)
        -- sim_g: if i = 0 and SIM generate
        --     CLK_SIM <= not CLK_SIM after 7 ps;

        --     process(CLK_SIM)
        --         variable v_bins     : STD_LOGIC_VECTOR(DEPTH*4-1 downto 0) := (others => '0');
        --         variable v_sensor   : STD_LOGIC := '0';
        --         variable cnt        : integer := 0;
        --         variable offset     : integer := 0;
        --     begin
        --         if rising_edge(CLK_SIM) then
        --             if CH = "ch2" then
        --                 offset := SIM_OFFSET;
        --             end if;

        --             v_bins := prop(v_bins);
        --             v_bins(0) := v_sensor;
        --             if cnt = 6000 + offset then
        --                 v_sensor := not v_sensor;
        --                 cnt := offset;
        --             else
        --                 cnt := cnt + 1;
        --             end if;
        --             BINS <= v_bins;
        --         end if;
        --     end process;
        -- end generate;

        -- Sampling flip-flops
        dff0: FDRE port map (
            Q   => S.bins_sync(4*i),
            C   => CLK_POL,
            CE  => '1',
            R   => '0',
            D   => BINS(4*i) );
        dff1: FDRE port map (
            Q   => S.bins_sync(4*i+1),
            C   => CLK_POL,
            CE  => '1',
            R   => '0',
            D   => BINS(4*i+1) );
        dff2: FDRE port map (
            Q   => S.bins_sync(4*i+2),
            C   => CLK_POL,
            CE  => '1',
            R   => '0',
            D   => BINS(4*i+2) );
        dff3: FDRE port map (
            Q   => S.bins_sync(4*i+3),
            C   => CLK_POL,
            CE  => '1',
            R   => '0',
            D   => BINS(4*i+3) );

    end generate;

end architecture DELAY_LINE_ARCH;