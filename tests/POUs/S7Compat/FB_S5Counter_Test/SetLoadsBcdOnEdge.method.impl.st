coUnit.TEST('SetLoadsBcdOnEdge');
AssertEquals_INT(Expected := 123, Actual := F_S5CounterSet(stCounter := stCounter, xRlo := TRUE, wBcd := 16#0123),
    Message := 'S C#123');
AssertEquals_WORD(Expected := 16#0123, Actual := F_S5CounterBcd(stCounter := stCounter), Message := 'LC C');
AssertEquals_WORD(Expected := 123, Actual := F_S5CounterBin(stCounter := stCounter), Message := 'L C');
AssertEquals_INT(Expected := 123, Actual := F_S5CounterSet(stCounter := stCounter, xRlo := TRUE, wBcd := 16#0456),
    Message := 'held: no load');
F_S5CounterSet(stCounter := stCounter, xRlo := FALSE, wBcd := 16#0456);
AssertEquals_INT(Expected := 456, Actual := F_S5CounterSet(stCounter := stCounter, xRlo := TRUE, wBcd := 16#0456),
    Message := 'edge: load');
coUnit.TEST_FINISHED();
