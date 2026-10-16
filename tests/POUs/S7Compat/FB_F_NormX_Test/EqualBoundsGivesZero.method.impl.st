coUnit.TEST('EqualBoundsGivesZero');

rResult := F_NormX(rMin := 5.0, rValue := 5.0, rMax := 5.0);
AssertEquals_REAL(Expected := 0.0,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'MIN = MAX gives defined value');

coUnit.TEST_FINISHED();
