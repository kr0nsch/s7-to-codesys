IF xRlo THEN
    stTimer.xRunning := FALSE;
    stTimer.xQ := FALSE;
    stTimer.tRest := T#0MS;
END_IF
F_S5Reset := stTimer.xQ;
