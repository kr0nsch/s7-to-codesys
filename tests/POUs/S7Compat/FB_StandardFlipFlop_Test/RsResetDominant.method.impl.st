coUnit.TEST('RsResetDominant');
fbDut(SET := TRUE, RESET1 := FALSE);
AssertTrue(Condition := fbDut.Q1, Message := 'SET alone: Q1 set');
fbDut(SET := TRUE, RESET1 := TRUE);
AssertFalse(Condition := fbDut.Q1, Message := 'SET=RESET1=TRUE: reset dominant');
fbDut(SET := FALSE, RESET1 := FALSE);
AssertFalse(Condition := fbDut.Q1, Message := 'inputs FALSE: Q1 holds FALSE');
coUnit.TEST_FINISHED();
