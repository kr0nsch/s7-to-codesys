coUnit.TEST('KeepsQWhileInHeldAcrossWrap');
GVL_S7Clock.xSimulation := TRUE;

GVL_S7Clock.tSimNow := T#0MS;
fbDut(IN := TRUE, PT := T#500MS);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 't=0 Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 't=0 ET');

GVL_S7Clock.tSimNow := T#600MS;
fbDut(IN := TRUE, PT := T#500MS);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 't=600 Q');
AssertEquals_TIME(Expected := T#500MS, Actual := fbDut.ET, Message := 't=600 ET');

GVL_S7Clock.tSimNow := T#49D17H2M47S;
fbDut(IN := TRUE, PT := T#500MS);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 'before wrap Q');
AssertEquals_TIME(Expected := T#500MS, Actual := fbDut.ET, Message := 'before wrap ET');

GVL_S7Clock.tSimNow := T#100MS;
fbDut(IN := TRUE, PT := T#500MS);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := 'after wrap Q');
AssertEquals_TIME(Expected := T#500MS, Actual := fbDut.ET, Message := 'after wrap ET');

GVL_S7Clock.tSimNow := T#200MS;
fbDut(IN := FALSE, PT := T#500MS);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 'IN off Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 'IN off ET');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
