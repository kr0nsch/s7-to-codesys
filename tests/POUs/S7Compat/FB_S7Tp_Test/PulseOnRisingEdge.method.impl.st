coUnit.TEST('PulseOnRisingEdge');
GVL_S7Clock.xSimulation := TRUE;

GVL_S7Clock.tSimNow := T#0MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=0 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=0 ET');

GVL_S7Clock.tSimNow := T#999MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=999 Q');
AssertEquals_TIME(Expected := T#999MS, Actual := fbDut.ET, Message := 't=999 ET');

GVL_S7Clock.tSimNow := T#1000MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=1000 Q');
AssertEquals_TIME(Expected := T#1000MS, Actual := fbDut.ET, Message := 't=1000 ET');

GVL_S7Clock.tSimNow := T#1500MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=1500 Q');
AssertEquals_TIME(Expected := T#1000MS, Actual := fbDut.ET, Message := 't=1500 ET');

GVL_S7Clock.tSimNow := T#1600MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=1600 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=1600 ET');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
