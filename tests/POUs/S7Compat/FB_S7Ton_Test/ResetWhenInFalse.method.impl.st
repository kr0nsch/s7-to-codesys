coUnit.TEST('ResetWhenInFalse');
GVL_S7Clock.xSimulation := TRUE;

GVL_S7Clock.tSimNow := T#0MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=0 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=0 ET');

GVL_S7Clock.tSimNow := T#1200MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=1200 Q');
AssertEquals_TIME(Expected := T#1000MS, Actual := fbDut.ET, Message := 't=1200 ET');

GVL_S7Clock.tSimNow := T#1300MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=1300 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=1300 ET');

GVL_S7Clock.tSimNow := T#1400MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=1400 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=1400 ET');

GVL_S7Clock.tSimNow := T#2399MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=2399 Q');
AssertEquals_TIME(Expected := T#999MS, Actual := fbDut.ET, Message := 't=2399 ET');

GVL_S7Clock.tSimNow := T#2400MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=2400 Q');
AssertEquals_TIME(Expected := T#1000MS, Actual := fbDut.ET, Message := 't=2400 ET');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
