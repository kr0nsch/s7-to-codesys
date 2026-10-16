coUnit.TEST('ReversedBoundsKeepsFormula');

rResult := F_ScaleX(rMin := 100.0, rValue := 0.25, rMax := 0.0);
AssertEquals_REAL(Expected := 75.0,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'MIN > MAX keeps the formula');

coUnit.TEST_FINISHED();
