stTimer.xQAtEnd := FALSE;
IF xRlo AND NOT stTimer.xRloStart THEN
    F_S5Start(stTimer := stTimer, wS5Time := wS5Time);
    stTimer.xQ := TRUE;
END_IF
stTimer.xRloStart := xRlo;
F_S5ExtPulse := stTimer.xQ;
