coUnit.TEST('ResetIsLevel');
F_S5CounterSet(stCounter := stCounter, xRlo := TRUE, wBcd := 16#0005);
AssertEquals_INT(Expected := 0, Actual := F_S5CounterReset(stCounter := stCounter, xRlo := TRUE), Message := 'R');
AssertEquals_INT(Expected := 1, Actual := F_S5CountUp(stCounter := stCounter, xRlo := TRUE), Message := 'CU edge');
AssertEquals_INT(Expected := 0, Actual := F_S5CounterReset(stCounter := stCounter, xRlo := TRUE), Message := 'R held');
AssertEquals_INT(Expected := 0, Actual := F_S5CounterReset(stCounter := stCounter, xRlo := FALSE), Message := 'R off');
AssertEquals_INT(Expected := 0, Actual := F_S5CountUp(stCounter := stCounter, xRlo := TRUE), Message := 'CU held');
coUnit.TEST_FINISHED();
