udiRest := TIME_TO_UDINT(F_S5Update(stTimer := stTimer));
udiBase := F_S5BaseMs(stTimer.wBase);
F_S5Bin := UDINT_TO_WORD((udiRest + udiBase - 1) / udiBase);
