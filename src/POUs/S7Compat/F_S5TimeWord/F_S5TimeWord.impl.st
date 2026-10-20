udiMs := TIME_TO_UDINT(tTime);
IF udiMs <= LIMIT_10MS THEN
    wBase := 0;
ELSIF udiMs <= LIMIT_100MS THEN
    wBase := 1;
ELSIF udiMs <= LIMIT_1S THEN
    wBase := 2;
ELSE
    wBase := BASE_10S;
END_IF
udiBaseMs := F_S5BaseMs(wBase);
udiUnits := MIN(udiMs / udiBaseMs, MAX_UNITS);
iUnits := UDINT_TO_INT(udiUnits);
F_S5TimeWord := SHL(wBase, BASE_SHIFT) OR F_S5ToBcd(iUnits);
