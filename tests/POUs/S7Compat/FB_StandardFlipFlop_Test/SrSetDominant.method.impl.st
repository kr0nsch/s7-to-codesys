coUnit.TEST('SrSetDominant');
fbDut(SET1 := TRUE, RESET := TRUE);
AssertTrue(Condition := fbDut.Q1, Message := 'SET1=RESET=TRUE: set dominant');
fbDut(SET1 := FALSE, RESET := FALSE);
AssertTrue(Condition := fbDut.Q1, Message := 'inputs FALSE: Q1 holds');
fbDut(SET1 := FALSE, RESET := TRUE);
AssertFalse(Condition := fbDut.Q1, Message := 'RESET alone: Q1 reset');
coUnit.TEST_FINISHED();
