coUnit.TEST('S7SrResetDominantViaRs');
fbDut(SET := TRUE, RESET1 := FALSE);
AssertTrue(Condition := fbDut.Q1, Message := 'S7 SR, S=1 R1=0: Q=1');
fbDut(SET := TRUE, RESET1 := TRUE);
AssertFalse(Condition := fbDut.Q1, Message := 'S7 SR, S=R1=1: reset dominant, Q=0');
coUnit.TEST_FINISHED();
