coUnit.TEST('ReversedBoundsKeepsFormula');

rResult := F_NormX(rMin := 100.0, rValue := 75.0, rMax := 0.0);
AssertEquals_REAL(Expected := 0.25,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'MIN > MAX keeps the formula');

coUnit.TEST_FINISHED();
