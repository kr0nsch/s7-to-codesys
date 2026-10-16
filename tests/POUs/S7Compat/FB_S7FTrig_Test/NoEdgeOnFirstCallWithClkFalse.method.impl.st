coUnit.TEST('NoEdgeOnFirstCallWithClkFalse');
fbDut(CLK := FALSE);
AssertFalse(Condition := fbDut.Q, Message := 'first call CLK=FALSE: no edge');
fbDut(CLK := FALSE);
AssertFalse(Condition := fbDut.Q, Message := 'second call CLK=FALSE: no edge');
coUnit.TEST_FINISHED();
