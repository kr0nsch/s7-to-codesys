coUnit.TEST('AboveMaxExtrapolates');

rResult := F_NormX(rMin := 0.0, rValue := 30412.8, rMax := 27648.0);
AssertEquals_REAL(Expected := 1.1,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'Above MAX extrapolates');

coUnit.TEST_FINISHED();
