coUnit.TEST('AtMaxGivesOne');

rResult := F_NormX(rMin := 0.0, rValue := 27648.0, rMax := 27648.0);
AssertEquals_REAL(Expected := 1.0,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'VALUE = MAX must give 1.0');

coUnit.TEST_FINISHED();
