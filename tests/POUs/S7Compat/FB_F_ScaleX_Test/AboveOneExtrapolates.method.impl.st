coUnit.TEST('AboveOneExtrapolates');

rResult := F_ScaleX(rMin := 0.0, rValue := 1.2, rMax := 100.0);
AssertEquals_REAL(Expected := 120.0,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'VALUE > 1.0 extrapolates');

coUnit.TEST_FINISHED();
