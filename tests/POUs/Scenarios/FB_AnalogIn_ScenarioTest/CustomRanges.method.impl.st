// AUTO-GENERATED — не редактировать: scenarios/FB_AnalogIn.csv, сценарий CustomRanges
coUnit.TEST('CustomRanges');
IF NOT xCustomRangesDone THEN
    xCustomRangesDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — шкала -50...150: четверть -> 0.0 = limitL
    GVL_S7Clock.tSimNow := T#0MS;
    fbCustomRanges.raw := 6912;
    fbCustomRanges.rangeLow := -50.0;
    fbCustomRanges.rangeHigh := 150.0;
    fbCustomRanges.limitHH := 120.0;
    fbCustomRanges.limitH := 100.0;
    fbCustomRanges.limitL := 0.0;
    fbCustomRanges.limitLL := -20.0;
    fbCustomRanges.hysteresis := 2.0;
    fbCustomRanges.substitute := 0.0;
    fbCustomRanges.simulation := FALSE;
    fbCustomRanges.simValue := 0.0;
    fbCustomRanges();
    AssertEquals_REAL(Expected := 0.0,
                      Actual := fbCustomRanges.value,
                      Delta := 0.001,
                      Message := 'CustomRanges#1 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.valid, Message := 'CustomRanges#1 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCustomRanges.channelFault,
                      Message := 'CustomRanges#1 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.overrange, Message := 'CustomRanges#1 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.underrange, Message := 'CustomRanges#1 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.alarmHH, Message := 'CustomRanges#1 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.warnH, Message := 'CustomRanges#1 warnH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.warnL, Message := 'CustomRanges#1 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.alarmLL, Message := 'CustomRanges#1 alarmLL');
    AssertEquals_WORD(Expected := 16#0041, Actual := fbCustomRanges.statusWord, Message := 'CustomRanges#1 statusWord');

    // #2, t = 100 мс — три четверти -> 100.0 = limitH; L сброшен
    GVL_S7Clock.tSimNow := T#100MS;
    fbCustomRanges.raw := 20736;
    fbCustomRanges();
    AssertEquals_REAL(Expected := 100.0,
                      Actual := fbCustomRanges.value,
                      Delta := 0.001,
                      Message := 'CustomRanges#2 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.valid, Message := 'CustomRanges#2 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCustomRanges.channelFault,
                      Message := 'CustomRanges#2 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.overrange, Message := 'CustomRanges#2 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.underrange, Message := 'CustomRanges#2 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.alarmHH, Message := 'CustomRanges#2 alarmHH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.warnH, Message := 'CustomRanges#2 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.warnL, Message := 'CustomRanges#2 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.alarmLL, Message := 'CustomRanges#2 alarmLL');
    AssertEquals_WORD(Expected := 16#0021, Actual := fbCustomRanges.statusWord, Message := 'CustomRanges#2 statusWord');

    // #3, t = 200 мс — максимум -> 150.0: HH и H
    GVL_S7Clock.tSimNow := T#200MS;
    fbCustomRanges.raw := 27648;
    fbCustomRanges();
    AssertEquals_REAL(Expected := 150.0,
                      Actual := fbCustomRanges.value,
                      Delta := 0.001,
                      Message := 'CustomRanges#3 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.valid, Message := 'CustomRanges#3 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCustomRanges.channelFault,
                      Message := 'CustomRanges#3 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.overrange, Message := 'CustomRanges#3 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.underrange, Message := 'CustomRanges#3 underrange');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.alarmHH, Message := 'CustomRanges#3 alarmHH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.warnH, Message := 'CustomRanges#3 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.warnL, Message := 'CustomRanges#3 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.alarmLL, Message := 'CustomRanges#3 alarmLL');
    AssertEquals_WORD(Expected := 16#0031, Actual := fbCustomRanges.statusWord, Message := 'CustomRanges#3 statusWord');

    // #4, t = 300 мс — минимум -> -50.0: L и LL
    GVL_S7Clock.tSimNow := T#300MS;
    fbCustomRanges.raw := 0;
    fbCustomRanges();
    AssertEquals_REAL(Expected := -50.0,
                      Actual := fbCustomRanges.value,
                      Delta := 0.001,
                      Message := 'CustomRanges#4 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.valid, Message := 'CustomRanges#4 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCustomRanges.channelFault,
                      Message := 'CustomRanges#4 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.overrange, Message := 'CustomRanges#4 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.underrange, Message := 'CustomRanges#4 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.alarmHH, Message := 'CustomRanges#4 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.warnH, Message := 'CustomRanges#4 warnH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.warnL, Message := 'CustomRanges#4 warnL');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.alarmLL, Message := 'CustomRanges#4 alarmLL');
    AssertEquals_WORD(Expected := 16#00C1, Actual := fbCustomRanges.statusWord, Message := 'CustomRanges#4 statusWord');

    // #5, t = 400 мс — обратная шкала 16...0: четверть -> 12.0 = limitH
    GVL_S7Clock.tSimNow := T#400MS;
    fbCustomRanges.raw := 6912;
    fbCustomRanges.rangeLow := 16.0;
    fbCustomRanges.rangeHigh := 0.0;
    fbCustomRanges.limitHH := 14.0;
    fbCustomRanges.limitH := 12.0;
    fbCustomRanges.limitL := 2.0;
    fbCustomRanges.limitLL := 1.0;
    fbCustomRanges.hysteresis := 0.5;
    fbCustomRanges();
    AssertEquals_REAL(Expected := 12.0,
                      Actual := fbCustomRanges.value,
                      Delta := 0.001,
                      Message := 'CustomRanges#5 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.valid, Message := 'CustomRanges#5 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCustomRanges.channelFault,
                      Message := 'CustomRanges#5 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.overrange, Message := 'CustomRanges#5 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.underrange, Message := 'CustomRanges#5 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.alarmHH, Message := 'CustomRanges#5 alarmHH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.warnH, Message := 'CustomRanges#5 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.warnL, Message := 'CustomRanges#5 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.alarmLL, Message := 'CustomRanges#5 alarmLL');
    AssertEquals_WORD(Expected := 16#0021, Actual := fbCustomRanges.statusWord, Message := 'CustomRanges#5 statusWord');

    // #6, t = 500 мс — обратная шкала: максимум raw -> 0.0, L и LL
    GVL_S7Clock.tSimNow := T#500MS;
    fbCustomRanges.raw := 27648;
    fbCustomRanges();
    AssertEquals_REAL(Expected := 0.0,
                      Actual := fbCustomRanges.value,
                      Delta := 0.001,
                      Message := 'CustomRanges#6 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.valid, Message := 'CustomRanges#6 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbCustomRanges.channelFault,
                      Message := 'CustomRanges#6 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.overrange, Message := 'CustomRanges#6 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.underrange, Message := 'CustomRanges#6 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.alarmHH, Message := 'CustomRanges#6 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbCustomRanges.warnH, Message := 'CustomRanges#6 warnH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.warnL, Message := 'CustomRanges#6 warnL');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbCustomRanges.alarmLL, Message := 'CustomRanges#6 alarmLL');
    AssertEquals_WORD(Expected := 16#00C1, Actual := fbCustomRanges.statusWord, Message := 'CustomRanges#6 statusWord');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
