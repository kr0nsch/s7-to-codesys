coUnit.TEST('RetOnDelayHoldsQUntilReset');
GVL_S7Clock.xSimulation := TRUE;
wPreset := F_S5TimeWord(T#1S);

GVL_S7Clock.tSimNow := T#0MS;
AssertFalse(Condition := F_S5RetOnDelay(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset), Message := 't=0 Q');

GVL_S7Clock.tSimNow := T#200MS;
AssertFalse(Condition := F_S5RetOnDelay(stTimer := stTimer, xRlo := FALSE, wS5Time := wPreset), Message := 't=200 Q');

GVL_S7Clock.tSimNow := T#1000MS;
AssertTrue(Condition := F_S5Q(stTimer := stTimer), Message := 't=1000 Q');

GVL_S7Clock.tSimNow := T#5000MS;
AssertTrue(Condition := F_S5RetOnDelay(stTimer := stTimer, xRlo := FALSE, wS5Time := wPreset), Message := 't=5000 Q');

GVL_S7Clock.tSimNow := T#5100MS;
AssertFalse(Condition := F_S5Reset(stTimer := stTimer, xRlo := TRUE), Message := 't=5100 R: Q');
AssertEquals_WORD(Expected := 0, Actual := F_S5Bin(stTimer := stTimer), Message := 't=5100 L T');
F_S5Reset(stTimer := stTimer, xRlo := FALSE);

GVL_S7Clock.tSimNow := T#5200MS;
F_S5RetOnDelay(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset);
AssertFalse(Condition := F_S5Q(stTimer := stTimer), Message := 't=5200 Q');

GVL_S7Clock.tSimNow := T#6200MS;
AssertTrue(Condition := F_S5Q(stTimer := stTimer), Message := 't=6200 Q');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
