coUnit.TEST('EnableRestartsRunningTimer');
GVL_S7Clock.xSimulation := TRUE;
wPreset := F_S5TimeWord(T#1S);

GVL_S7Clock.tSimNow := T#0MS;
F_S5ExtPulse(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset);

GVL_S7Clock.tSimNow := T#500MS;
F_S5Enable(stTimer := stTimer, xRlo := TRUE);
F_S5ExtPulse(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset);
AssertEquals_WORD(Expected := 100, Actual := F_S5Bin(stTimer := stTimer), Message := 't=500 FR restart');

GVL_S7Clock.tSimNow := T#1400MS;
AssertTrue(Condition := F_S5Q(stTimer := stTimer), Message := 't=1400 Q');

GVL_S7Clock.tSimNow := T#1500MS;
AssertFalse(Condition := F_S5Q(stTimer := stTimer), Message := 't=1500 Q');

GVL_S7Clock.tSimNow := T#1600MS;
F_S5Enable(stTimer := stTimer, xRlo := FALSE);
AssertFalse(Condition := F_S5ExtPulse(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset),
    Message := 't=1600 FR fall');

GVL_S7Clock.tSimNow := T#1700MS;
F_S5Enable(stTimer := stTimer, xRlo := TRUE);
AssertTrue(Condition := F_S5ExtPulse(stTimer := stTimer, xRlo := TRUE, wS5Time := wPreset),
    Message := 't=1700 FR edge');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
