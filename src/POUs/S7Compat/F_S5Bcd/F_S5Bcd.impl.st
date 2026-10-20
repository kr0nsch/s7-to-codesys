iUnits := WORD_TO_INT(F_S5Bin(stTimer := stTimer));
F_S5Bcd := SHL(stTimer.wBase, BASE_SHIFT) OR F_S5ToBcd(iUnits);
