coUnit.TEST('AdvancesLikeStandardTimer');
IF NOT xRtDone THEN
    fbRtReference(IN := TRUE, PT := T_RT_REF_PT);
    IF NOT xRtStarted THEN
        xRtStarted := TRUE;
        tRtStart := F_S7Now();
    END_IF
    tRtElapsed := F_S7Now() - tRtStart;
    IF fbRtReference.ET >= T_RT_DURATION THEN
        xRtDone := TRUE;
        IF tRtElapsed >= fbRtReference.ET THEN
            tRtDiff := tRtElapsed - fbRtReference.ET;
        ELSE
            tRtDiff := fbRtReference.ET - tRtElapsed;
        END_IF
        AssertTrue(Condition := tRtDiff <= T_RT_TOL, Message := 'F_S7Now advances like Standard TON ET');
    END_IF
END_IF
IF xRtDone THEN
    coUnit.TEST_FINISHED();
END_IF
