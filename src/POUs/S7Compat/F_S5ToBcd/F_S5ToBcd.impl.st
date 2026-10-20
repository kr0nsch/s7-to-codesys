wUnits := INT_TO_WORD(iValue MOD TEN);
wTens := INT_TO_WORD((iValue / TEN) MOD TEN);
wHundreds := INT_TO_WORD((iValue / HUNDRED) MOD TEN);
F_S5ToBcd := wUnits OR SHL(wTens, TENS_SHIFT) OR SHL(wHundreds, HUNDREDS_SHIFT);
