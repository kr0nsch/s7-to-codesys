coUnit.TEST('RetriggerIgnored');
GVL_S7Clock.xSimulation := TRUE;

GVL_S7Clock.tSimNow := T#0MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=0 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=0 ET');

GVL_S7Clock.tSimNow := T#200MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=200 Q');
AssertEquals_TIME(Expected := T#200MS, Actual := fbDut.ET, Message := 't=200 ET');

GVL_S7Clock.tSimNow := T#400MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=400 Q');
AssertEquals_TIME(Expected := T#400MS, Actual := fbDut.ET, Message := 't=400 ET');

GVL_S7Clock.tSimNow := T#1000MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=1000 Q');
AssertEquals_TIME(Expected := T#1000MS, Actual := fbDut.ET, Message := 't=1000 ET');

GVL_S7Clock.tSimNow := T#1100MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=1100 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=1100 ET');

GVL_S7Clock.tSimNow := T#1200MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=1200 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=1200 ET');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
