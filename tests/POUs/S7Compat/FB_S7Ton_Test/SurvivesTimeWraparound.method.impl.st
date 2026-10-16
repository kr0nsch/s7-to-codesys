coUnit.TEST('SurvivesTimeWraparound');
GVL_S7Clock.xSimulation := TRUE;

GVL_S7Clock.tSimNow := T#49D17H2M47S;
fbDut(IN := TRUE, PT := T#500MS);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := 'start Q');
AssertEquals_TIME(Expected := T#0MS, Actual := fbDut.ET, Message := 'start ET');

GVL_S7Clock.tSimNow := T#40MS;
fbDut(IN := TRUE, PT := T#500MS);
AssertEquals_BOOL(Expected := FALSE, Actual := fbDut.Q, Message := '+336ms Q');
AssertEquals_TIME(Expected := T#336MS, Actual := fbDut.ET, Message := '+336ms ET');

GVL_S7Clock.tSimNow := T#300MS;
fbDut(IN := TRUE, PT := T#500MS);
AssertEquals_BOOL(Expected := TRUE, Actual := fbDut.Q, Message := '+596ms Q');
AssertEquals_TIME(Expected := T#500MS, Actual := fbDut.ET, Message := '+596ms ET');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
