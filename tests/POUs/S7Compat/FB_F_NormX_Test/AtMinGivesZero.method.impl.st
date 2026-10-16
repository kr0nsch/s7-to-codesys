coUnit.TEST('AtMinGivesZero');

rResult := F_NormX(rMin := 0.0, rValue := 0.0, rMax := 27648.0);
AssertEquals_REAL(Expected := 0.0,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'VALUE = MIN must give 0.0');

coUnit.TEST_FINISHED();
