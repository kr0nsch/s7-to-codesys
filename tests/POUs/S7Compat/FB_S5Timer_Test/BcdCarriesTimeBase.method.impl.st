coUnit.TEST('BcdCarriesTimeBase');
GVL_S7Clock.xSimulation := TRUE;
wPreset := F_S5TimeWord(T#20S);
AssertEquals_WORD(Expected := 16#1200, Actual := wPreset, Message := 'S5T#20S');

GVL_S7Clock.tSimNow := T#0MS;
F_S5OnDelay(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset);
AssertEquals_WORD(Expected := 16#1200, Actual := F_S5Bcd(stTimer := stTimer), Message := 't=0 LC T');
AssertEquals_WORD(Expected := 200, Actual := F_S5Bin(stTimer := stTimer), Message := 't=0 L T');

GVL_S7Clock.tSimNow := T#5000MS;
AssertEquals_WORD(Expected := 16#1150, Actual := F_S5Bcd(stTimer := stTimer), Message := 't=5000 LC T');
AssertEquals_WORD(Expected := 150, Actual := F_S5Bin(stTimer := stTimer), Message := 't=5000 L T');

GVL_S7Clock.tSimNow := T#5050MS;
AssertEquals_WORD(Expected := 150, Actual := F_S5Bin(stTimer := stTimer), Message := 't=5050 L T rounds up');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
