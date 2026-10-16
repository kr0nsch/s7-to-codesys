// AUTO-GENERATED — не редактировать: scenarios/FB_Totalizer.csv, сценарий PulseVolumeZero
coUnit.TEST('PulseVolumeZero');
IF NOT xPulseVolumeZeroDone THEN
    xPulseVolumeZeroDone := TRUE;
    GVL_S7Clock.xSimulation := TRUE;

    // #1, t = 0 мс — 1.0 м3, импульсов нет
    GVL_S7Clock.tSimNow := T#0MS;
    fbPulseVolumeZero.flow := 3600.0;
    fbPulseVolumeZero.cycleTime := T#1000MS;
    fbPulseVolumeZero.lowFlowCutoff := 0.5;
    fbPulseVolumeZero.enable := TRUE;
    fbPulseVolumeZero.reset := FALSE;
    fbPulseVolumeZero.pulseVolume := 0.0;
    fbPulseVolumeZero();
    AssertEquals_LREAL(Expected := 1.0,
                       Actual := fbPulseVolumeZero.total,
                       Delta := 0.000001,
                       Message := 'PulseVolumeZero#1 total');
    AssertEquals_LREAL(Expected := 1.0,
                       Actual := fbPulseVolumeZero.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'PulseVolumeZero#1 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbPulseVolumeZero.pulseCount, Message := 'PulseVolumeZero#1 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbPulseVolumeZero.pulse, Message := 'PulseVolumeZero#1 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPulseVolumeZero.cutoffActive,
                      Message := 'PulseVolumeZero#1 cutoffActive');

    // #2, t = 1000 мс — 2.0 м3, импульсов нет
    GVL_S7Clock.tSimNow := T#1000MS;
    fbPulseVolumeZero();
    AssertEquals_LREAL(Expected := 2.0,
                       Actual := fbPulseVolumeZero.total,
                       Delta := 0.000001,
                       Message := 'PulseVolumeZero#2 total');
    AssertEquals_LREAL(Expected := 2.0,
                       Actual := fbPulseVolumeZero.lifetimeTotal,
                       Delta := 0.000001,
                       Message := 'PulseVolumeZero#2 lifetimeTotal');
    AssertEquals_DINT(Expected := 0, Actual := fbPulseVolumeZero.pulseCount, Message := 'PulseVolumeZero#2 pulseCount');
    AssertEquals_BOOL(Expected := FALSE, Actual := fbPulseVolumeZero.pulse, Message := 'PulseVolumeZero#2 pulse');
    AssertEquals_BOOL(Expected := FALSE,
                      Actual := fbPulseVolumeZero.cutoffActive,
                      Message := 'PulseVolumeZero#2 cutoffActive');

    GVL_S7Clock.xSimulation := FALSE;
END_IF
coUnit.TEST_FINISHED();
