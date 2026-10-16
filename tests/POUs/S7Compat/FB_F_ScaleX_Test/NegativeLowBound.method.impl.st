coUnit.TEST('NegativeLowBound');

rResult := F_ScaleX(rMin := -50.0, rValue := 0.75, rMax := 50.0);
AssertEquals_REAL(Expected := 25.0,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'Range -50..50 at 0.75 gives 25');

coUnit.TEST_FINISHED();
