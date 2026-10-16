coUnit.TEST('MidRangeGivesHalf');

rResult := F_NormX(rMin := 0.0, rValue := 13824.0, rMax := 27648.0);
AssertEquals_REAL(Expected := 0.5,
                  Actual := rResult,
                  Delta := R_DELTA,
                  Message := 'Mid range must give 0.5');

coUnit.TEST_FINISHED();
