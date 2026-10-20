coUnit.TEST('SupervisionHoldsUntilAck');
FOR iCycle := 1 TO CYCLES DO
    fbDut(xStart := TRUE);
END_FOR
FOR iCycle := 1 TO CYCLES DO
    fbDut(xStart := FALSE, xValveFault := TRUE);
END_FOR
AssertTrue(Condition := fbDut.ERR_FLT, Message := 'supervision error');

FOR iCycle := 1 TO CYCLES DO
    fbDut(xValveFault := FALSE, xLevelLow := TRUE, xShortWash := TRUE);
END_FOR
AssertTrue(Condition := fbDut.ERR_FLT, Message := 'error latched');
AssertTrue(Condition := fbDut.xDrainValve, Message := 'transition blocked: still Drain');
AssertFalse(Condition := fbDut.xWashPump, Message := 'no QuickRinse yet');

FOR iCycle := 1 TO CYCLES DO
    fbDut(ACK_EF := TRUE);
END_FOR
AssertFalse(Condition := fbDut.ERR_FLT, Message := 'acknowledged');
AssertFalse(Condition := fbDut.xDrainValve, Message := 'Drain left');
AssertTrue(Condition := fbDut.xWashPump, Message := 'QuickRinse');
coUnit.TEST_FINISHED();
