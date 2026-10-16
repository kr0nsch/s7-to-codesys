coUnit.TEST('HalfGivesMidRange');

rResult := F_ScaleX(rMin := 0.0, rValue := 0.5, rMax := 100.0);
AssertEquals_REAL(Expected := 50.0,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := '0.5 must give mid range');

coUnit.TEST_FINISHED();
