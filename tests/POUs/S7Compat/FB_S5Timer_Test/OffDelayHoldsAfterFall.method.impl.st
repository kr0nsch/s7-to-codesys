coUnit.TEST('OffDelayHoldsAfterFall');
GVL_S7Clock.xSimulation := TRUE;
wPreset := F_S5TimeWord(T#1S);

GVL_S7Clock.tSimNow := T#0MS;
F_S5OffDelay(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset);
AssertTrue(Condition := F_S5Q(stTimer := stTimer), Message := 't=0 Q');

GVL_S7Clock.tSimNow := T#100MS;
AssertTrue(Condition := F_S5OffDelay(stTimer := stTimer, xRlo := FALSE, wS5Time := wPreset), Message := 't=100 Q');

GVL_S7Clock.tSimNow := T#600MS;
AssertTrue(Condition := F_S5OffDelay(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset), Message := 't=600 Q');
AssertEquals_WORD(Expected := 50, Actual := F_S5Bin(stTimer := stTimer), Message := 't=600 L T stopped');

GVL_S7Clock.tSimNow := T#700MS;
AssertTrue(Condition := F_S5OffDelay(stTimer := stTimer, xRlo := FALSE, wS5Time := wPreset), Message := 't=700 Q');

GVL_S7Clock.tSimNow := T#1699MS;
AssertTrue(Condition := F_S5Q(stTimer := stTimer), Message := 't=1699 Q');

GVL_S7Clock.tSimNow := T#1700MS;
AssertFalse(Condition := F_S5Q(stTimer := stTimer), Message := 't=1700 Q');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
