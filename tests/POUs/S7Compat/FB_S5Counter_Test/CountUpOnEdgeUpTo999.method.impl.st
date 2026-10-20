coUnit.TEST('CountUpOnEdgeUpTo999');
AssertEquals_INT(Expected := 1, Actual := F_S5CountUp(stCounter := stCounter, xRlo := TRUE), Message := 'edge 1');
AssertEquals_INT(Expected := 1, Actual := F_S5CountUp(stCounter := stCounter, xRlo := TRUE), Message := 'held');
F_S5CountUp(stCounter := stCounter, xRlo := FALSE);
AssertEquals_INT(Expected := 2, Actual := F_S5CountUp(stCounter := stCounter, xRlo := TRUE), Message := 'edge 2');
AssertEquals_INT(Expected := 999, Actual := F_S5CounterSet(stCounter := stCounter, xRlo := TRUE, wBcd := 16#0999),
    Message := 'S 999');
F_S5CountUp(stCounter := stCounter, xRlo := FALSE);
AssertEquals_INT(Expected := 999, Actual := F_S5CountUp(stCounter := stCounter, xRlo := TRUE), Message := 'limit');
coUnit.TEST_FINISHED();
