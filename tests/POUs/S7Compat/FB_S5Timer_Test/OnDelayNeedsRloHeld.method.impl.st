coUnit.TEST('OnDelayNeedsRloHeld');
GVL_S7Clock.xSimulation := TRUE;
wPreset := F_S5TimeWord(T#1S);

GVL_S7Clock.tSimNow := T#0MS;
AssertFalse(Condition := F_S5OnDelay(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset), Message := 't=0 Q');

GVL_S7Clock.tSimNow := T#999MS;
AssertFalse(Condition := F_S5Q(stTimer := stTimer), Message := 't=999 Q');
AssertEquals_WORD(Expected := 1, Actual := F_S5Bin(stTimer := stTimer), Message := 't=999 L T');

GVL_S7Clock.tSimNow := T#1000MS;
AssertTrue(Condition := F_S5Q(stTimer := stTimer), Message := 't=1000 Q');

GVL_S7Clock.tSimNow := T#1100MS;
AssertFalse(Condition := F_S5OnDelay(stTimer := stTimer, xRlo := FALSE, wS5Time := wPreset), Message := 't=1100 Q');

GVL_S7Clock.tSimNow := T#1200MS;
F_S5OnDelay(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset);

GVL_S7Clock.tSimNow := T#1500MS;
AssertFalse(Condition := F_S5OnDelay(stTimer := stTimer, xRlo := FALSE, wS5Time := wPreset), Message := 't=1500 Q');
AssertEquals_WORD(Expected := 70, Actual := F_S5Bin(stTimer := stTimer), Message := 't=1500 L T frozen');

GVL_S7Clock.tSimNow := T#2500MS;
AssertFalse(Condition := F_S5Q(stTimer := stTimer), Message := 't=2500 stopped: Q');
AssertEquals_WORD(Expected := 70, Actual := F_S5Bin(stTimer := stTimer), Message := 't=2500 L T frozen');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
