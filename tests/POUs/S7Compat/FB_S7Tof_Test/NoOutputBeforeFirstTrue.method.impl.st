coUnit.TEST('NoOutputBeforeFirstTrue');
GVL_S7Clock.xSimulation := TRUE;

GVL_S7Clock.tSimNow := T#0MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=0 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=0 ET');

GVL_S7Clock.tSimNow := T#2000MS;
fbDut(IN := FALSE, PT := T#1S);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=2000 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=2000 ET');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
