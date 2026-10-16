coUnit.TEST('ZeroGivesMin');

rResult := F_ScaleX(rMin := 20.0, rValue := 0.0, rMax := 80.0);
AssertEquals_REAL(Expected := 20.0,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'VALUE = 0.0 must give MIN');

coUnit.TEST_FINISHED();
