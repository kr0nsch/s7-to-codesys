coUnit.TEST('MatchesStandardInRealTime');
IF NOT xRtDone THEN
    IF NOT xRtStarted THEN
        xRtStarted := TRUE;
        tRtStart := F_S7Now();  // xSimulation = FALSE: время ПЛК, как TIME()
    END_IF
    tRtElapsed := F_S7Now() - tRtStart;
    xRtIn := (tRtElapsed < T#100MS) OR (tRtElapsed >= T#150MS AND tRtElapsed < T#500MS);
    fbRtCompat(IN := xRtIn, PT := T_RT_PT);
    fbRtStandard(IN := xRtIn, PT := T_RT_PT);
    IF fbRtCompat.ET >= fbRtStandard.ET THEN
        tRtEtDiff := fbRtCompat.ET - fbRtStandard.ET;
    ELSE
        tRtEtDiff := fbRtStandard.ET - fbRtCompat.ET;
    END_IF
    tRtEtToPt := T_RT_PT - fbRtStandard.ET;  // ET <= PT
    IF tRtEtDiff > T_RT_TOL OR (fbRtCompat.Q <> fbRtStandard.Q AND tRtEtToPt > T_RT_TOL) THEN
        iRtMismatches := iRtMismatches + 1;
    END_IF
    xRtSawQ := xRtSawQ OR fbRtStandard.Q;
    IF tRtElapsed >= T_RT_DURATION THEN
        xRtDone := TRUE;
        AssertEquals_INT(Expected := 0, Actual := iRtMismatches, Message := 'FB_S7Tp vs TP: mismatching cycles');
        AssertTrue(Condition := xRtSawQ, Message := 'FB_S7Tp vs TP: Standard Q never TRUE, test did not run');
    END_IF
END_IF
IF xRtDone THEN
    coUnit.TEST_FINISHED();
END_IF
