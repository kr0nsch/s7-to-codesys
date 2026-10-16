coUnit.TEST('ZeroPtSwitchesImmediately');
GVL_S7Clock.xSimulation := TRUE;

GVL_S7Clock.tSimNow := T#100MS;
fbDut(IN := TRUE, PT := T#0MS);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=100 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=100 ET');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
