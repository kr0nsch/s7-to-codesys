// AUTO-GENERATED — не редактировать: scenarios/FB_AnalogIn.csv, сценарий ScalingPoints
coUnit.TEST('ScalingPoints');
IF NOT xScalingPointsDone THEN
    xScalingPointsDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — 0 -> 0.0 бар; ниже L и LL
    GVL_S7Clock.tSimNow := T#0MS;
    fbScalingPoints.raw := 0;
    fbScalingPoints.rangeLow := 0.0;
    fbScalingPoints.rangeHigh := 16.0;
    fbScalingPoints.limitHH := 14.0;
    fbScalingPoints.limitH := 12.0;
    fbScalingPoints.limitL := 2.0;
    fbScalingPoints.limitLL := 1.0;
    fbScalingPoints.hysteresis := 0.5;
    fbScalingPoints.substitute := 0.0;
    fbScalingPoints.simulation := FALSE;
    fbScalingPoints.simValue := 0.0;
    fbScalingPoints();
    AssertEquals_REAL(Expected := 0.0,
                      Actual := fbScalingPoints.value,
                      Delta := 0.001,
                      Message := 'ScalingPoints#1 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.valid, Message := 'ScalingPoints#1 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbScalingPoints.channelFault,
                      Message := 'ScalingPoints#1 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.overrange, Message := 'ScalingPoints#1 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.underrange, Message := 'ScalingPoints#1 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.alarmHH, Message := 'ScalingPoints#1 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.warnH, Message := 'ScalingPoints#1 warnH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.warnL, Message := 'ScalingPoints#1 warnL');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.alarmLL, Message := 'ScalingPoints#1 alarmLL');
    AssertEquals_WORD(Expected := 16#00C1,
                      Actual := fbScalingPoints.statusWord,
                      Message := 'ScalingPoints#1 statusWord');

    // #2, t = 100 мс — середина шкалы -> 8.0; L и LL сброшены (8.0 > 2.5 и > 1.5)
    GVL_S7Clock.tSimNow := T#100MS;
    fbScalingPoints.raw := 13824;
    fbScalingPoints();
    AssertEquals_REAL(Expected := 8.0,
                      Actual := fbScalingPoints.value,
                      Delta := 0.001,
                      Message := 'ScalingPoints#2 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.valid, Message := 'ScalingPoints#2 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbScalingPoints.channelFault,
                      Message := 'ScalingPoints#2 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.overrange, Message := 'ScalingPoints#2 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.underrange, Message := 'ScalingPoints#2 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.alarmHH, Message := 'ScalingPoints#2 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.warnH, Message := 'ScalingPoints#2 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.warnL, Message := 'ScalingPoints#2 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.alarmLL, Message := 'ScalingPoints#2 alarmLL');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbScalingPoints.statusWord,
                      Message := 'ScalingPoints#2 statusWord');

    // #3, t = 200 мс — номинальный максимум -> 16.0; HH и H
    GVL_S7Clock.tSimNow := T#200MS;
    fbScalingPoints.raw := 27648;
    fbScalingPoints();
    AssertEquals_REAL(Expected := 16.0,
                      Actual := fbScalingPoints.value,
                      Delta := 0.001,
                      Message := 'ScalingPoints#3 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.valid, Message := 'ScalingPoints#3 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbScalingPoints.channelFault,
                      Message := 'ScalingPoints#3 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.overrange, Message := 'ScalingPoints#3 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.underrange, Message := 'ScalingPoints#3 underrange');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.alarmHH, Message := 'ScalingPoints#3 alarmHH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.warnH, Message := 'ScalingPoints#3 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.warnL, Message := 'ScalingPoints#3 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.alarmLL, Message := 'ScalingPoints#3 alarmLL');
    AssertEquals_WORD(Expected := 16#0031,
                      Actual := fbScalingPoints.statusWord,
                      Message := 'ScalingPoints#3 statusWord');

    // #4, t = 300 мс — четверть -> 4.0; HH и H сброшены
    GVL_S7Clock.tSimNow := T#300MS;
    fbScalingPoints.raw := 6912;
    fbScalingPoints();
    AssertEquals_REAL(Expected := 4.0,
                      Actual := fbScalingPoints.value,
                      Delta := 0.001,
                      Message := 'ScalingPoints#4 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.valid, Message := 'ScalingPoints#4 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbScalingPoints.channelFault,
                      Message := 'ScalingPoints#4 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.overrange, Message := 'ScalingPoints#4 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.underrange, Message := 'ScalingPoints#4 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.alarmHH, Message := 'ScalingPoints#4 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.warnH, Message := 'ScalingPoints#4 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.warnL, Message := 'ScalingPoints#4 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.alarmLL, Message := 'ScalingPoints#4 alarmLL');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbScalingPoints.statusWord,
                      Message := 'ScalingPoints#4 statusWord');

    // #5, t = 400 мс — -> 12.0 = limitH: H включается (>=)
    GVL_S7Clock.tSimNow := T#400MS;
    fbScalingPoints.raw := 20736;
    fbScalingPoints();
    AssertEquals_REAL(Expected := 12.0,
                      Actual := fbScalingPoints.value,
                      Delta := 0.001,
                      Message := 'ScalingPoints#5 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.valid, Message := 'ScalingPoints#5 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbScalingPoints.channelFault,
                      Message := 'ScalingPoints#5 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.overrange, Message := 'ScalingPoints#5 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.underrange, Message := 'ScalingPoints#5 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.alarmHH, Message := 'ScalingPoints#5 alarmHH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.warnH, Message := 'ScalingPoints#5 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.warnL, Message := 'ScalingPoints#5 warnL');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.alarmLL, Message := 'ScalingPoints#5 alarmLL');
    AssertEquals_WORD(Expected := 16#0021,
                      Actual := fbScalingPoints.statusWord,
                      Message := 'ScalingPoints#5 statusWord');

    // #6, t = 500 мс — -> 1.0 = limitLL: L и LL включаются (<=), H сброшен
    GVL_S7Clock.tSimNow := T#500MS;
    fbScalingPoints.raw := 1728;
    fbScalingPoints();
    AssertEquals_REAL(Expected := 1.0,
                      Actual := fbScalingPoints.value,
                      Delta := 0.001,
                      Message := 'ScalingPoints#6 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.valid, Message := 'ScalingPoints#6 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbScalingPoints.channelFault,
                      Message := 'ScalingPoints#6 channelFault');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.overrange, Message := 'ScalingPoints#6 overrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.underrange, Message := 'ScalingPoints#6 underrange');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.alarmHH, Message := 'ScalingPoints#6 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbScalingPoints.warnH, Message := 'ScalingPoints#6 warnH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.warnL, Message := 'ScalingPoints#6 warnL');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbScalingPoints.alarmLL, Message := 'ScalingPoints#6 alarmLL');
    AssertEquals_WORD(Expected := 16#00C1,
                      Actual := fbScalingPoints.statusWord,
                      Message := 'ScalingPoints#6 statusWord');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
