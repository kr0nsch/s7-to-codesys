coUnit.TEST('RsSetHeldReappliesAfterReset');
fbDut(SET := TRUE, RESET1 := FALSE);
AssertTrue(Condition := fbDut.Q1, Message := 'SET=TRUE: Q1 set');
fbDut(SET := TRUE, RESET1 := TRUE);
AssertFalse(Condition := fbDut.Q1, Message := 'RESET1 pulse: Q1 reset');
fbDut(SET := TRUE, RESET1 := FALSE);
AssertTrue(Condition := fbDut.Q1, Message := 'SET still TRUE after RESET1: level semantics, Q1 set again');
coUnit.TEST_FINISHED();
