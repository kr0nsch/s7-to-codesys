coUnit.TEST('BelowZeroExtrapolates');

rResult := F_ScaleX(rMin := 0.0, rValue := -0.25, rMax := 100.0);
AssertEquals_REAL(Expected := -25.0,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'VALUE < 0.0 extrapolates');

coUnit.TEST_FINISHED();
