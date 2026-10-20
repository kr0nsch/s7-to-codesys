coUnit.TEST('QReadBeforeStartSeesPreviousState');
GVL_S7Clock.xSimulation := TRUE;
wPreset := F_S5TimeWord(T#1S);

GVL_S7Clock.tSimNow := T#0MS;
F_S5OnDelay(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset);

GVL_S7Clock.tSimNow := T#1000MS;
AssertTrue(Condition := F_S5Q(stTimer := stTimer), Message := 'read before SD');
F_S5OnDelay(stTimer := stTimer, xRlo := FALSE, wS5Time := wPreset);
AssertFalse(Condition := F_S5Q(stTimer := stTimer), Message := 'read after SD with RLO=0');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
