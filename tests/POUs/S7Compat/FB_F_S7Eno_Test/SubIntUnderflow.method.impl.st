coUnit.TEST('SubIntUnderflow');
AssertFalse(Condition := F_S7EnoSubInt(iIn1 := -32768, iIn2 := 1), Message := 'SUB_I -32768 - 1: ENO=FALSE');
AssertTrue(Condition := F_S7EnoSubInt(iIn1 := -32767, iIn2 := 1), Message := 'SUB_I -32767 - 1: ENO=TRUE');
coUnit.TEST_FINISHED();
