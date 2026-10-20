coUnit.TEST('ExtPulseRunsOutAndRetriggers');
GVL_S7Clock.xSimulation := TRUE;
wPreset := F_S5TimeWord(T#1S);

GVL_S7Clock.tSimNow := T#0MS;
F_S5ExtPulse(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset);
AssertTrue(Condition := F_S5Q(stTimer := stTimer), Message := 't=0 Q');

GVL_S7Clock.tSimNow := T#100MS;
AssertTrue(Condition := F_S5ExtPulse(stTimer := stTimer, xRlo := FALSE, wS5Time := wPreset), Message := 't=100 Q');

GVL_S7Clock.tSimNow := T#600MS;
AssertTrue(Condition := F_S5ExtPulse(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset), Message := 't=600 Q');
AssertEquals_WORD(Expected := 100, Actual := F_S5Bin(stTimer := stTimer), Message := 't=600 retrigger');

GVL_S7Clock.tSimNow := T#1599MS;
AssertTrue(Condition := F_S5Q(stTimer := stTimer), Message := 't=1599 Q');
AssertEquals_WORD(Expected := 1, Actual := F_S5Bin(stTimer := stTimer), Message := 't=1599 L T');

GVL_S7Clock.tSimNow := T#1600MS;
AssertFalse(Condition := F_S5Q(stTimer := stTimer), Message := 't=1600 Q');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
