coUnit.TEST('HoldsThenDrops');
GVL_S7Clock.xSimulation := TRUE;

GVL_S7Clock.tSimNow := T#0MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=0 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=0 ET');

GVL_S7Clock.tSimNow := T#100MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=100 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=100 ET');

GVL_S7Clock.tSimNow := T#1099MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=1099 Q');
AssertEquals_TIME(Expected := T#999MS, Actual := fbDut.ET, Message := 't=1099 ET');

GVL_S7Clock.tSimNow := T#1100MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=1100 Q');
AssertEquals_TIME(Expected := T#1000MS, Actual := fbDut.ET, Message := 't=1100 ET');

GVL_S7Clock.tSimNow := T#5000MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=5000 Q');
AssertEquals_TIME(Expected := T#1000MS, Actual := fbDut.ET, Message := 't=5000 ET');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
