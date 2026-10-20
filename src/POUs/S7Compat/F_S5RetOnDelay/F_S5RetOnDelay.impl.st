stTimer.xQAtEnd := TRUE;
IF xRlo AND NOT stTimer.xRloStart THEN
    F_S5Start(stTimer := stTimer, wS5Time := wS5Time);
END_IF
stTimer.xRloStart := xRlo;
F_S5RetOnDelay := stTimer.xQ;
