// AUTO-GENERATED — не редактировать: scenarios/FB_AnalogIn.csv, сценарий ChannelDiagnostics
coUnit.TEST('ChannelDiagnostics');
IF NOT xChannelDiagnosticsDone THEN
    xChannelDiagnosticsDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — норма 8.0; замещающее значение 5.0
    GVL_S7Clock.tSimNow := T#0MS;
    fbChannelDiagnostics.raw := 13824;
    fbChannelDiagnostics.rangeLow := 0.0;
    fbChannelDiagnostics.rangeHigh := 16.0;
    fbChannelDiagnostics.limitHH := 14.0;
    fbChannelDiagnostics.limitH := 12.0;
    fbChannelDiagnostics.limitL := 2.0;
    fbChannelDiagnostics.limitLL := 1.0;
    fbChannelDiagnostics.hysteresis := 0.5;
    fbChannelDiagnostics.substitute := 5.0;
    fbChannelDiagnostics.simulation := FALSE;
    fbChannelDiagnostics.simValue := 0.0;
    fbChannelDiagnostics();
    AssertEquals_REAL(Expected := 8.0,
                      Actual := fbChannelDiagnostics.value,
                      Delta := 0.001,
                      Message := 'ChannelDiagnostics#1 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbChannelDiagnostics.valid, Message := 'ChannelDiagnostics#1 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.channelFault,
                      Message := 'ChannelDiagnostics#1 channelFault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.overrange,
                      Message := 'ChannelDiagnostics#1 overrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.underrange,
                      Message := 'ChannelDiagnostics#1 underrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmHH,
                      Message := 'ChannelDiagnostics#1 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnH, Message := 'ChannelDiagnostics#1 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnL, Message := 'ChannelDiagnostics#1 warnL');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmLL,
                      Message := 'ChannelDiagnostics#1 alarmLL');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbChannelDiagnostics.statusWord,
                      Message := 'ChannelDiagnostics#1 statusWord');

    // #2, t = 100 мс — выше номинала: overrange, value ограничено 16.0, HH и H
    GVL_S7Clock.tSimNow := T#100MS;
    fbChannelDiagnostics.raw := 27649;
    fbChannelDiagnostics();
    AssertEquals_REAL(Expected := 16.0,
                      Actual := fbChannelDiagnostics.value,
                      Delta := 0.001,
                      Message := 'ChannelDiagnostics#2 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbChannelDiagnostics.valid, Message := 'ChannelDiagnostics#2 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.channelFault,
                      Message := 'ChannelDiagnostics#2 channelFault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbChannelDiagnostics.overrange,
                      Message := 'ChannelDiagnostics#2 overrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.underrange,
                      Message := 'ChannelDiagnostics#2 underrange');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbChannelDiagnostics.alarmHH,
                      Message := 'ChannelDiagnostics#2 alarmHH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbChannelDiagnostics.warnH, Message := 'ChannelDiagnostics#2 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnL, Message := 'ChannelDiagnostics#2 warnL');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmLL,
                      Message := 'ChannelDiagnostics#2 alarmLL');
    AssertEquals_WORD(Expected := 16#0035,
                      Actual := fbChannelDiagnostics.statusWord,
                      Message := 'ChannelDiagnostics#2 statusWord');

    // #3, t = 200 мс — верхняя граница зоны перегрузки — ещё не неисправность
    GVL_S7Clock.tSimNow := T#200MS;
    fbChannelDiagnostics.raw := 32511;
    fbChannelDiagnostics();
    AssertEquals_REAL(Expected := 16.0,
                      Actual := fbChannelDiagnostics.value,
                      Delta := 0.001,
                      Message := 'ChannelDiagnostics#3 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbChannelDiagnostics.valid, Message := 'ChannelDiagnostics#3 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.channelFault,
                      Message := 'ChannelDiagnostics#3 channelFault');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbChannelDiagnostics.overrange,
                      Message := 'ChannelDiagnostics#3 overrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.underrange,
                      Message := 'ChannelDiagnostics#3 underrange');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbChannelDiagnostics.alarmHH,
                      Message := 'ChannelDiagnostics#3 alarmHH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbChannelDiagnostics.warnH, Message := 'ChannelDiagnostics#3 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnL, Message := 'ChannelDiagnostics#3 warnL');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmLL,
                      Message := 'ChannelDiagnostics#3 alarmLL');
    AssertEquals_WORD(Expected := 16#0035,
                      Actual := fbChannelDiagnostics.statusWord,
                      Message := 'ChannelDiagnostics#3 statusWord');

    // #4, t = 300 мс — за зоной перегрузки: channelFault, value := substitute, уставки сброшены
    GVL_S7Clock.tSimNow := T#300MS;
    fbChannelDiagnostics.raw := 32512;
    fbChannelDiagnostics();
    AssertEquals_REAL(Expected := 5.0,
                      Actual := fbChannelDiagnostics.value,
                      Delta := 0.001,
                      Message := 'ChannelDiagnostics#4 value');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.valid, Message := 'ChannelDiagnostics#4 valid');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbChannelDiagnostics.channelFault,
                      Message := 'ChannelDiagnostics#4 channelFault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.overrange,
                      Message := 'ChannelDiagnostics#4 overrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.underrange,
                      Message := 'ChannelDiagnostics#4 underrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmHH,
                      Message := 'ChannelDiagnostics#4 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnH, Message := 'ChannelDiagnostics#4 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnL, Message := 'ChannelDiagnostics#4 warnL');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmLL,
                      Message := 'ChannelDiagnostics#4 alarmLL');
    AssertEquals_WORD(Expected := 16#0002,
                      Actual := fbChannelDiagnostics.statusWord,
                      Message := 'ChannelDiagnostics#4 statusWord');

    // #5, t = 400 мс — переполнение/обрыв (7FFF)
    GVL_S7Clock.tSimNow := T#400MS;
    fbChannelDiagnostics.raw := 32767;
    fbChannelDiagnostics();
    AssertEquals_REAL(Expected := 5.0,
                      Actual := fbChannelDiagnostics.value,
                      Delta := 0.001,
                      Message := 'ChannelDiagnostics#5 value');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.valid, Message := 'ChannelDiagnostics#5 valid');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbChannelDiagnostics.channelFault,
                      Message := 'ChannelDiagnostics#5 channelFault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.overrange,
                      Message := 'ChannelDiagnostics#5 overrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.underrange,
                      Message := 'ChannelDiagnostics#5 underrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmHH,
                      Message := 'ChannelDiagnostics#5 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnH, Message := 'ChannelDiagnostics#5 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnL, Message := 'ChannelDiagnostics#5 warnL');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmLL,
                      Message := 'ChannelDiagnostics#5 alarmLL');
    AssertEquals_WORD(Expected := 16#0002,
                      Actual := fbChannelDiagnostics.statusWord,
                      Message := 'ChannelDiagnostics#5 statusWord');

    // #6, t = 500 мс — канал восстановлен: 8.0, уставки снова считаются (HH не держится)
    GVL_S7Clock.tSimNow := T#500MS;
    fbChannelDiagnostics.raw := 13824;
    fbChannelDiagnostics();
    AssertEquals_REAL(Expected := 8.0,
                      Actual := fbChannelDiagnostics.value,
                      Delta := 0.001,
                      Message := 'ChannelDiagnostics#6 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbChannelDiagnostics.valid, Message := 'ChannelDiagnostics#6 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.channelFault,
                      Message := 'ChannelDiagnostics#6 channelFault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.overrange,
                      Message := 'ChannelDiagnostics#6 overrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.underrange,
                      Message := 'ChannelDiagnostics#6 underrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmHH,
                      Message := 'ChannelDiagnostics#6 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnH, Message := 'ChannelDiagnostics#6 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnL, Message := 'ChannelDiagnostics#6 warnL');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmLL,
                      Message := 'ChannelDiagnostics#6 alarmLL');
    AssertEquals_WORD(Expected := 16#0001,
                      Actual := fbChannelDiagnostics.statusWord,
                      Message := 'ChannelDiagnostics#6 statusWord');

    // #7, t = 600 мс — ниже номинала: underrange, value ограничено 0.0, L и LL
    GVL_S7Clock.tSimNow := T#600MS;
    fbChannelDiagnostics.raw := -1;
    fbChannelDiagnostics();
    AssertEquals_REAL(Expected := 0.0,
                      Actual := fbChannelDiagnostics.value,
                      Delta := 0.001,
                      Message := 'ChannelDiagnostics#7 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbChannelDiagnostics.valid, Message := 'ChannelDiagnostics#7 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.channelFault,
                      Message := 'ChannelDiagnostics#7 channelFault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.overrange,
                      Message := 'ChannelDiagnostics#7 overrange');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbChannelDiagnostics.underrange,
                      Message := 'ChannelDiagnostics#7 underrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmHH,
                      Message := 'ChannelDiagnostics#7 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnH, Message := 'ChannelDiagnostics#7 warnH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbChannelDiagnostics.warnL, Message := 'ChannelDiagnostics#7 warnL');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbChannelDiagnostics.alarmLL,
                      Message := 'ChannelDiagnostics#7 alarmLL');
    AssertEquals_WORD(Expected := 16#00C9,
                      Actual := fbChannelDiagnostics.statusWord,
                      Message := 'ChannelDiagnostics#7 statusWord');

    // #8, t = 700 мс — нижняя граница зоны перегрузки — ещё не неисправность
    GVL_S7Clock.tSimNow := T#700MS;
    fbChannelDiagnostics.raw := -4864;
    fbChannelDiagnostics();
    AssertEquals_REAL(Expected := 0.0,
                      Actual := fbChannelDiagnostics.value,
                      Delta := 0.001,
                      Message := 'ChannelDiagnostics#8 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbChannelDiagnostics.valid, Message := 'ChannelDiagnostics#8 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.channelFault,
                      Message := 'ChannelDiagnostics#8 channelFault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.overrange,
                      Message := 'ChannelDiagnostics#8 overrange');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbChannelDiagnostics.underrange,
                      Message := 'ChannelDiagnostics#8 underrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmHH,
                      Message := 'ChannelDiagnostics#8 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnH, Message := 'ChannelDiagnostics#8 warnH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbChannelDiagnostics.warnL, Message := 'ChannelDiagnostics#8 warnL');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbChannelDiagnostics.alarmLL,
                      Message := 'ChannelDiagnostics#8 alarmLL');
    AssertEquals_WORD(Expected := 16#00C9,
                      Actual := fbChannelDiagnostics.statusWord,
                      Message := 'ChannelDiagnostics#8 statusWord');

    // #9, t = 800 мс — за зоной: channelFault
    GVL_S7Clock.tSimNow := T#800MS;
    fbChannelDiagnostics.raw := -4865;
    fbChannelDiagnostics();
    AssertEquals_REAL(Expected := 5.0,
                      Actual := fbChannelDiagnostics.value,
                      Delta := 0.001,
                      Message := 'ChannelDiagnostics#9 value');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.valid, Message := 'ChannelDiagnostics#9 valid');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbChannelDiagnostics.channelFault,
                      Message := 'ChannelDiagnostics#9 channelFault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.overrange,
                      Message := 'ChannelDiagnostics#9 overrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.underrange,
                      Message := 'ChannelDiagnostics#9 underrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmHH,
                      Message := 'ChannelDiagnostics#9 alarmHH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnH, Message := 'ChannelDiagnostics#9 warnH');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbChannelDiagnostics.warnL, Message := 'ChannelDiagnostics#9 warnL');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmLL,
                      Message := 'ChannelDiagnostics#9 alarmLL');
    AssertEquals_WORD(Expected := 16#0002,
                      Actual := fbChannelDiagnostics.statusWord,
                      Message := 'ChannelDiagnostics#9 statusWord');

    // #10, t = 900 мс — антипереполнение (8000)
    GVL_S7Clock.tSimNow := T#900MS;
    fbChannelDiagnostics.raw := -32768;
    fbChannelDiagnostics();
    AssertEquals_REAL(Expected := 5.0,
                      Actual := fbChannelDiagnostics.value,
                      Delta := 0.001,
                      Message := 'ChannelDiagnostics#10 value');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.valid,
                      Message := 'ChannelDiagnostics#10 valid');
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbChannelDiagnostics.channelFault,
                      Message := 'ChannelDiagnostics#10 channelFault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.overrange,
                      Message := 'ChannelDiagnostics#10 overrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.underrange,
                      Message := 'ChannelDiagnostics#10 underrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmHH,
                      Message := 'ChannelDiagnostics#10 alarmHH');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.warnH,
                      Message := 'ChannelDiagnostics#10 warnH');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.warnL,
                      Message := 'ChannelDiagnostics#10 warnL');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmLL,
                      Message := 'ChannelDiagnostics#10 alarmLL');
    AssertEquals_WORD(Expected := 16#0002,
                      Actual := fbChannelDiagnostics.statusWord,
                      Message := 'ChannelDiagnostics#10 statusWord');

    // #11, t = 1000 мс — канал восстановлен: 2.0 — только L
    GVL_S7Clock.tSimNow := T#1000MS;
    fbChannelDiagnostics.raw := 3456;
    fbChannelDiagnostics();
    AssertEquals_REAL(Expected := 2.0,
                      Actual := fbChannelDiagnostics.value,
                      Delta := 0.001,
                      Message := 'ChannelDiagnostics#11 value');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbChannelDiagnostics.valid, Message := 'ChannelDiagnostics#11 valid');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.channelFault,
                      Message := 'ChannelDiagnostics#11 channelFault');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.overrange,
                      Message := 'ChannelDiagnostics#11 overrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.underrange,
                      Message := 'ChannelDiagnostics#11 underrange');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmHH,
                      Message := 'ChannelDiagnostics#11 alarmHH');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.warnH,
                      Message := 'ChannelDiagnostics#11 warnH');
    AssertEquals_BOOL(Expected := TRUE, Actual := fbChannelDiagnostics.warnL, Message := 'ChannelDiagnostics#11 warnL');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbChannelDiagnostics.alarmLL,
                      Message := 'ChannelDiagnostics#11 alarmLL');
    AssertEquals_WORD(Expected := 16#0041,
                      Actual := fbChannelDiagnostics.statusWord,
                      Message := 'ChannelDiagnostics#11 statusWord');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
