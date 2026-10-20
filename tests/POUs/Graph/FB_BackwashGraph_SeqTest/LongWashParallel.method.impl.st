coUnit.TEST('LongWashParallel');
FOR iCycle := 1 TO CYCLES DO
    fbDut(xStart := TRUE);
END_FOR
AssertTrue(Condition := fbDut.xDrainValve, Message := 'Drain');

FOR iCycle := 1 TO CYCLES DO
    fbDut(xStart := FALSE, xLevelLow := TRUE);
END_FOR
AssertFalse(Condition := fbDut.xDrainValve, Message := 'parallel: drain closed');
AssertTrue(Condition := fbDut.xBlower, Message := 'parallel: Air blower');
AssertTrue(Condition := fbDut.xWashPump, Message := 'parallel: Rinse pump');
AssertFalse(Condition := fbDut.xAirValve, Message := 'D 2 s not elapsed');
AssertTrue(Condition := fbDut.xWashActive, Message := 'wash active');
coUnit.TEST_FINISHED();
