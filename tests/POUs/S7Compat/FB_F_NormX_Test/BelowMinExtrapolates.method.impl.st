coUnit.TEST('BelowMinExtrapolates');

rResult := F_NormX(rMin := 0.0, rValue := -2764.8, rMax := 27648.0);
AssertEquals_REAL(Expected := -0.1,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'Below MIN extrapolates');

coUnit.TEST_FINISHED();
