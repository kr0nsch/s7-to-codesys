coUnit.TEST('CountsFromRisingEdge');
GVL_S7Clock.xSimulation := TRUE;

GVL_S7Clock.tSimNow := T#0MS;
fbDut(IN := FALSE, PT := T#2S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=0 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=0 ET');

GVL_S7Clock.tSimNow := T#1000MS;
fbDut(IN := TRUE, PT := T#2S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=1000 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=1000 ET');

GVL_S7Clock.tSimNow := T#2999MS;
fbDut(IN := TRUE, PT := T#2S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=2999 Q');
AssertEquals_TIME(Expected := T#1999MS, Actual := fbDut.ET, Message := 't=2999 ET');

GVL_S7Clock.tSimNow := T#3000MS;
fbDut(IN := TRUE, PT := T#2S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=3000 Q');
AssertEquals_TIME(Expected := T#2000MS, Actual := fbDut.ET, Message := 't=3000 ET');

GVL_S7Clock.tSimNow := T#9000MS;
fbDut(IN := TRUE, PT := T#2S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=9000 Q');
AssertEquals_TIME(Expected := T#2000MS, Actual := fbDut.ET, Message := 't=9000 ET');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
