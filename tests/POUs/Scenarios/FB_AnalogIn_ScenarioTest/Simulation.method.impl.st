// AUTO-GENERATED — не редактировать: scenarios/FB_AnalogIn.csv, сценарий Simulation
coUnit.TEST('Simulation');
IF NOT xSimulationDone THEN
    xSimulationDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — неисправность, value = substitute 0.0
    GVL_S7Clock.tSimNow := T#0MS;
    fbSimulation.raw := 32767;
    fbSimulation.rangeLow := 0.0;
    fbSimulation.rangeHigh := 16.0;
    fbSimulation.limitHH := 14.0;
    fbSimulation.limitH := 12.0;
    fbSimulation.limitL := 2.0;
    fbSimulation.limitLL := 1.0;
    fbSimulation.hysteresis := 0.5;
    fbSimulation.substitute := 0.0;
    fbSimulation.simulation := FALSE;
    fbSimulation.simValue := 0.0;
    fbSimulation();
    AssertEquals_REAL(Expected := 0.0, Actual := fbSimulation.value, Delta := 0.001, Message := 'Simulation#1 value');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.valid, Message := 'Simulation#1 valid');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSimulation.channelFault, Message := 'Simulation#1 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.overrange, Message := 'Simulation#1 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.underrange, Message := 'Simulation#1 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.alarmHH, Message := 'Simulation#1 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.warnH, Message := 'Simulation#1 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.warnL, Message := 'Simulation#1 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.alarmLL, Message := 'Simulation#1 alarmLL');
    AssertEquals_WORD(Expected := 16#0002, Actual := fbSimulation.statusWord, Message := 'Simulation#1 statusWord');

    // #2, t = 100 мс — имитация 15.0: valid, HH и H; channelFault по raw остаётся
    GVL_S7Clock.tSimNow := T#100MS;
    fbSimulation.simulation := TRUE;
    fbSimulation.simValue := 15.0;
    fbSimulation();
    AssertEquals_REAL(Expected := 15.0, Actual := fbSimulation.value, Delta := 0.001, Message := 'Simulation#2 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSimulation.valid, Message := 'Simulation#2 valid');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSimulation.channelFault, Message := 'Simulation#2 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.overrange, Message := 'Simulation#2 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.underrange, Message := 'Simulation#2 underrange');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSimulation.alarmHH, Message := 'Simulation#2 alarmHH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSimulation.warnH, Message := 'Simulation#2 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.warnL, Message := 'Simulation#2 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.alarmLL, Message := 'Simulation#2 alarmLL');
    AssertEquals_WORD(Expected := 16#0133, Actual := fbSimulation.statusWord, Message := 'Simulation#2 statusWord');

    // #3, t = 200 мс — 13.0 < 13.5: HH сброшен, H держится
    GVL_S7Clock.tSimNow := T#200MS;
    fbSimulation.simValue := 13.0;
    fbSimulation();
    AssertEquals_REAL(Expected := 13.0, Actual := fbSimulation.value, Delta := 0.001, Message := 'Simulation#3 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSimulation.valid, Message := 'Simulation#3 valid');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSimulation.channelFault, Message := 'Simulation#3 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.overrange, Message := 'Simulation#3 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.underrange, Message := 'Simulation#3 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.alarmHH, Message := 'Simulation#3 alarmHH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSimulation.warnH, Message := 'Simulation#3 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.warnL, Message := 'Simulation#3 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.alarmLL, Message := 'Simulation#3 alarmLL');
    AssertEquals_WORD(Expected := 16#0123, Actual := fbSimulation.statusWord, Message := 'Simulation#3 statusWord');

    // #4, t = 300 мс — канал исправен, имитация продолжается: value 13.0
    GVL_S7Clock.tSimNow := T#300MS;
    fbSimulation.raw := 13824;
    fbSimulation();
    AssertEquals_REAL(Expected := 13.0, Actual := fbSimulation.value, Delta := 0.001, Message := 'Simulation#4 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSimulation.valid, Message := 'Simulation#4 valid');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.channelFault, Message := 'Simulation#4 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.overrange, Message := 'Simulation#4 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.underrange, Message := 'Simulation#4 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.alarmHH, Message := 'Simulation#4 alarmHH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSimulation.warnH, Message := 'Simulation#4 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.warnL, Message := 'Simulation#4 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.alarmLL, Message := 'Simulation#4 alarmLL');
    AssertEquals_WORD(Expected := 16#0121, Actual := fbSimulation.statusWord, Message := 'Simulation#4 statusWord');

    // #5, t = 400 мс — имитация снята: value по raw 8.0, H сброшен
    GVL_S7Clock.tSimNow := T#400MS;
    fbSimulation.simulation := FALSE;
    fbSimulation();
    AssertEquals_REAL(Expected := 8.0, Actual := fbSimulation.value, Delta := 0.001, Message := 'Simulation#5 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbSimulation.valid, Message := 'Simulation#5 valid');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.channelFault, Message := 'Simulation#5 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.overrange, Message := 'Simulation#5 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.underrange, Message := 'Simulation#5 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.alarmHH, Message := 'Simulation#5 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.warnH, Message := 'Simulation#5 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.warnL, Message := 'Simulation#5 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbSimulation.alarmLL, Message := 'Simulation#5 alarmLL');
    AssertEquals_WORD(Expected := 16#0001, Actual := fbSimulation.statusWord, Message := 'Simulation#5 statusWord');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
