coUnit.TEST('ShortWashCycle');
FOR iCycle := 1 TO CYCLES DO
    fbDut();
END_FOR
AssertTrue(Condition := fbDut.xReady, Message := 'Idle: ready');
AssertFalse(Condition := fbDut.xDrainValve, Message := 'Idle: drain closed');

FOR iCycle := 1 TO CYCLES DO
    fbDut(xStart := TRUE);
END_FOR
AssertFalse(Condition := fbDut.xReady, Message := 'Drain: not ready');
AssertTrue(Condition := fbDut.xDrainValve, Message := 'Drain: drain open');
AssertTrue(Condition := fbDut.xWashActive, Message := 'Drain: S wash active');
AssertTrue(Condition := fbDut.xValvesBusy, Message := 'Drain: post operation');
AssertEquals_INT(Expected := 1, Actual := fbDut.iWashCount, Message := 'Drain: S1 count once');

FOR iCycle := 1 TO CYCLES DO
    fbDut(xStart := FALSE, xLevelLow := TRUE, xShortWash := TRUE);
END_FOR
AssertFalse(Condition := fbDut.xDrainValve, Message := 'QuickRinse: drain closed');
AssertTrue(Condition := fbDut.xWashPump, Message := 'QuickRinse: pump');
AssertFalse(Condition := fbDut.xBlower, Message := 'QuickRinse: no blower');

FOR iCycle := 1 TO CYCLES DO
    fbDut(xLevelLow := FALSE, xLevelHigh := TRUE);
END_FOR
AssertTrue(Condition := fbDut.xReady, Message := 'back to Idle');
AssertFalse(Condition := fbDut.xWashPump, Message := 'Idle: pump off');
AssertFalse(Condition := fbDut.xInletValve, Message := 'Idle: inlet closed');
AssertFalse(Condition := fbDut.xWashActive, Message := 'Refill: R wash active');
AssertEquals_INT(Expected := 1, Actual := fbDut.iWashCount, Message := 'one wash');
coUnit.TEST_FINISHED();
