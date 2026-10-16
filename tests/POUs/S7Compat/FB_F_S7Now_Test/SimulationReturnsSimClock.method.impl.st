coUnit.TEST('SimulationReturnsSimClock');
GVL_S7Clock.xSimulation := TRUE;
GVL_S7Clock.tSimNow := T#12345MS;
AssertEquals_TIME(Expected := T#12345MS, Actual := F_S7Now(), Message := 'simulated clock');
GVL_S7Clock.xSimulation := FALSE;
coUnit.TEST_FINISHED();
