coUnit.TEST('ReturnBeforeTimeout');
GVL_S7Clock.xSimulation := TRUE;

GVL_S7Clock.tSimNow := T#0MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=0 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=0 ET');

GVL_S7Clock.tSimNow := T#100MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=100 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=100 ET');

GVL_S7Clock.tSimNow := T#600MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=600 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=600 ET');

GVL_S7Clock.tSimNow := T#700MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=700 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=700 ET');

GVL_S7Clock.tSimNow := T#1699MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=1699 Q');
AssertEquals_TIME(Expected := T#999MS, Actual := fbDut.ET, Message := 't=1699 ET');

GVL_S7Clock.tSimNow := T#1700MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=1700 Q');
AssertEquals_TIME(Expected := T#1000MS, Actual := fbDut.ET, Message := 't=1700 ET');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
