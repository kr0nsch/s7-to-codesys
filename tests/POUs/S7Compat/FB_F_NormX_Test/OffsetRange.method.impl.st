coUnit.TEST('OffsetRange');

rResult := F_NormX(rMin := 4.0, rValue := 12.0, rMax := 20.0);
AssertEquals_REAL(Expected := 0.5,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := '4..20 mA midpoint must give 0.5');

coUnit.TEST_FINISHED();
