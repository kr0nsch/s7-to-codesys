coUnit.TEST('ResetIsLevelAndNeedsNewEdge');
GVL_S7Clock.xSimulation := TRUE;
wPreset := F_S5TimeWord(T#1S);

GVL_S7Clock.tSimNow := T#0MS;
F_S5OnDelay(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset);
AssertFalse(Condition := F_S5Reset(stTimer := stTimer, xRlo := TRUE), Message := 't=0 R');

GVL_S7Clock.tSimNow := T#2000MS;
F_S5OnDelay(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset);
F_S5Reset(stTimer := stTimer, xRlo := FALSE);
AssertFalse(Condition := F_S5Q(stTimer := stTimer), Message := 't=2000 no restart without edge');

GVL_S7Clock.tSimNow := T#2100MS;
F_S5OnDelay(stTimer := stTimer, xRlo := FALSE, wS5Time := wPreset);

GVL_S7Clock.tSimNow := T#2200MS;
F_S5OnDelay(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset);

GVL_S7Clock.tSimNow := T#3200MS;
AssertTrue(Condition := F_S5Q(stTimer := stTimer), Message := 't=3200 Q');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
