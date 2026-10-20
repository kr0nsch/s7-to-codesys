coUnit.TEST('PulseStopsWhenRloFalls');
GVL_S7Clock.xSimulation := TRUE;
wPreset := F_S5TimeWord(T#1S);

GVL_S7Clock.tSimNow := T#0MS;
AssertTrue(Condition := F_S5Pulse(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset), Message := 't=0 Q');
AssertEquals_WORD(Expected := 100, Actual := F_S5Bin(stTimer := stTimer), Message := 't=0 L T');

GVL_S7Clock.tSimNow := T#500MS;
AssertTrue(Condition := F_S5Pulse(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset), Message := 't=500 Q');
AssertEquals_WORD(Expected := 50, Actual := F_S5Bin(stTimer := stTimer), Message := 't=500 L T');

GVL_S7Clock.tSimNow := T#1000MS;
AssertFalse(Condition := F_S5Q(stTimer := stTimer), Message := 't=1000 time out: Q');
AssertEquals_WORD(Expected := 0, Actual := F_S5Bin(stTimer := stTimer), Message := 't=1000 L T');

GVL_S7Clock.tSimNow := T#1200MS;
AssertFalse(Condition := F_S5Pulse(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset), Message := 't=1200 no edge');

GVL_S7Clock.tSimNow := T#1300MS;
F_S5Pulse(stTimer := stTimer, xRlo := FALSE, wS5Time := wPreset);

GVL_S7Clock.tSimNow := T#1400MS;
AssertTrue(Condition := F_S5Pulse(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset), Message := 't=1400 edge');

GVL_S7Clock.tSimNow := T#1500MS;
AssertFalse(Condition := F_S5Pulse(stTimer := stTimer, xRlo := FALSE, wS5Time := wPreset), Message := 't=1500 stop');
AssertEquals_WORD(Expected := 90, Actual := F_S5Bin(stTimer := stTimer), Message := 't=1500 L T frozen');

GVL_S7Clock.tSimNow := T#3000MS;
AssertEquals_WORD(Expected := 90, Actual := F_S5Bin(stTimer := stTimer), Message := 't=3000 L T frozen');
AssertFalse(Condition := F_S5Q(stTimer := stTimer), Message := 't=3000 Q');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
