IF xRlo AND NOT stTimer.xRloFree THEN
    stTimer.xRloStart := FALSE;
END_IF
stTimer.xRloFree := xRlo;
F_S5Enable := stTimer.xQ;
