stTimer.wBase := SHR(wS5Time, BASE_SHIFT) AND BASE_MASK;
udiUnits := INT_TO_UDINT(F_S5FromBcd(wS5Time));
udiBaseMs := F_S5BaseMs(stTimer.wBase);
stTimer.tPreset := UDINT_TO_TIME(udiUnits * udiBaseMs);
stTimer.tStart := F_S7Now();
stTimer.tRest := stTimer.tPreset;
stTimer.xRunning := TRUE;
F_S5Start := TRUE;
