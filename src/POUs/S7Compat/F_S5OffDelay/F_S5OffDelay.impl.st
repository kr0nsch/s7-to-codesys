stTimer.xQAtEnd := FALSE;
IF xRlo AND NOT stTimer.xRloStart THEN
    F_S5Update(stTimer := stTimer);
    stTimer.xRunning := FALSE;
    stTimer.xQ := TRUE;
END_IF
IF NOT xRlo AND stTimer.xRloStart THEN
    F_S5Start(stTimer := stTimer, wS5Time := wS5Time);
    stTimer.xQ := TRUE;
END_IF
stTimer.xRloStart := xRlo;
F_S5OffDelay := stTimer.xQ;
