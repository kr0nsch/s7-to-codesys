wUnits := wBcd AND NIBBLE;
wTens := SHR(wBcd, TENS_SHIFT) AND NIBBLE;
wHundreds := SHR(wBcd, HUNDREDS_SHIFT) AND NIBBLE;
F_S5FromBcd := WORD_TO_INT(wUnits) + TEN * WORD_TO_INT(wTens) + HUNDRED * WORD_TO_INT(wHundreds);
