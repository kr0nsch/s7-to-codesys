coUnit.TEST('InitResets');
FOR iCycle := 1 TO CYCLES DO
    fbDut(xStart := TRUE);
END_FOR
AssertTrue(Condition := fbDut.xDrainValve, Message := 'Drain');

FOR iCycle := 1 TO CYCLES DO
    fbDut(INIT_SQ := TRUE);
END_FOR
AssertTrue(Condition := fbDut.xReady, Message := 'INIT_SQ: Idle');
AssertFalse(Condition := fbDut.xDrainValve, Message := 'INIT_SQ: drain closed');

FOR iCycle := 1 TO CYCLES DO
    fbDut(INIT_SQ := FALSE, xStart := TRUE);
END_FOR
AssertTrue(Condition := fbDut.xDrainValve, Message := 'restart: Drain');
AssertEquals_INT(Expected := 2, Actual := fbDut.iWashCount, Message := 'wash #2');
coUnit.TEST_FINISHED();
