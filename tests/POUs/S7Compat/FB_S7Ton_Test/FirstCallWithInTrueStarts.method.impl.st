coUnit.TEST('FirstCallWithInTrueStarts');
GVL_S7Clock.xSimulation := TRUE;

GVL_S7Clock.tSimNow := T#500MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=500 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=500 ET');

GVL_S7Clock.tSimNow := T#1499MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=1499 Q');
AssertEquals_TIME(Expected := T#999MS, Actual := fbDut.ET, Message := 't=1499 ET');

GVL_S7Clock.tSimNow := T#1500MS;
fbDut(IN := TRUE, PT := T#1S);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=1500 Q');
AssertEquals_TIME(Expected := T#1000MS, Actual := fbDut.ET, Message := 't=1500 ET');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
