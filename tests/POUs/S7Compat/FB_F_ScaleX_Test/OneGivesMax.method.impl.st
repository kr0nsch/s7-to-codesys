coUnit.TEST('OneGivesMax');

rResult := F_ScaleX(rMin := 20.0, rValue := 1.0, rMax := 80.0);
AssertEquals_REAL(Expected := 80.0,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'VALUE = 1.0 must give MAX');

coUnit.TEST_FINISHED();
