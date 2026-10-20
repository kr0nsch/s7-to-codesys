coUnit.TEST('InterlockStopsPump');
FOR iCycle := 1 TO CYCLES DO
    fbDut(xStart := TRUE);
END_FOR
FOR iCycle := 1 TO CYCLES DO
    fbDut(xStart := FALSE, xLevelLow := TRUE);
END_FOR
AssertTrue(Condition := fbDut.xWashPump, Message := 'Rinse: pump');

FOR iCycle := 1 TO CYCLES DO
    fbDut(xLevelLow := FALSE, xPumpOk := FALSE);
END_FOR
AssertFalse(Condition := fbDut.xWashPump, Message := 'interlock not met: pump off');
AssertTrue(Condition := fbDut.xBlower, Message := 'Air keeps running');

FOR iCycle := 1 TO CYCLES DO
    fbDut(xPumpOk := TRUE);
END_FOR
AssertTrue(Condition := fbDut.xWashPump, Message := 'interlock met: pump on');
coUnit.TEST_FINISHED();
