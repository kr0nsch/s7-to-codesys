coUnit.TEST('S7RsSetDominantViaSr');
fbDut(SET1 := FALSE, RESET := TRUE);
AssertFalse(Condition := fbDut.Q1, Message := 'S7 RS, R=1 S1=0: Q=0');
fbDut(SET1 := TRUE, RESET := TRUE);
AssertTrue(Condition := fbDut.Q1, Message := 'S7 RS, R=S1=1: set dominant, Q=1');
coUnit.TEST_FINISHED();
