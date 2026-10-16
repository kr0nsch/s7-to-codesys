coUnit.TEST('EqualBoundsGivesMin');

rResult := F_ScaleX(rMin := 10.0, rValue := 0.5, rMax := 10.0);
AssertEquals_REAL(Expected := 10.0,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'MIN = MAX gives defined value');

coUnit.TEST_FINISHED();
