coUnit.TEST('MulIntOverflow');
AssertFalse(Condition := F_S7EnoMulInt(iIn1 := 200, iIn2 := 200), Message := 'MUL_I 200 * 200: ENO=FALSE');
AssertTrue(Condition := F_S7EnoMulInt(iIn1 := 181, iIn2 := 181), Message := 'MUL_I 181 * 181: ENO=TRUE');
AssertFalse(Condition := F_S7EnoMulInt(iIn1 := -32768, iIn2 := -1), Message := 'MUL_I -32768 * -1: ENO=FALSE');
coUnit.TEST_FINISHED();
