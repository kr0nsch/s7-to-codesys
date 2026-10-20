stTimer.xQAtEnd := TRUE;
IF xRlo THEN
    IF NOT stTimer.xRloStart THEN
        F_S5Start(stTimer := stTimer, wS5Time := wS5Time);
    END_IF
ELSE
    F_S5Update(stTimer := stTimer);
    stTimer.xRunning := FALSE;
    stTimer.xQ := FALSE;
END_IF
stTimer.xRloStart := xRlo;
F_S5OnDelay := stTimer.xQ;
