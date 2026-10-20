IF stTimer.xRunning THEN
    tElapsed := F_S7Now() - stTimer.tStart;
    IF tElapsed >= stTimer.tPreset THEN
        stTimer.xRunning := FALSE;
        stTimer.xQ := stTimer.xQAtEnd;
        stTimer.tRest := T#0MS;
    ELSE
        stTimer.tRest := stTimer.tPreset - tElapsed;
    END_IF
END_IF
F_S5Update := stTimer.tRest;
