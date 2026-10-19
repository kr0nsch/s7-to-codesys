coUnit.TEST('CtudResetBeatsLoad');
fbDut(CU := FALSE, CD := FALSE, RESET := FALSE, LOAD := TRUE, PV := 3);
AssertEquals_WORD(Expected := 3, Actual := fbDut.CV, Message := 'LOAD: CV=PV');
AssertTrue(Condition := fbDut.QU, Message := 'CV=PV: QU=TRUE');
fbDut(CU := FALSE, CD := FALSE, RESET := TRUE, LOAD := TRUE, PV := 3);
AssertEquals_WORD(Expected := 0, Actual := fbDut.CV, Message := 'RESET and LOAD: RESET wins, CV=0');
AssertTrue(Condition := fbDut.QD, Message := 'CV=0: QD=TRUE');
AssertFalse(Condition := fbDut.QU, Message := 'CV=0 < PV: QU=FALSE');
coUnit.TEST_FINISHED();
