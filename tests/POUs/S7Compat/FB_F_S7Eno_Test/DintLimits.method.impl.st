coUnit.TEST('DintLimits');
AssertFalse(Condition := F_S7EnoAddDint(diIn1 := 2147483647, diIn2 := 1), Message := 'ADD_D max + 1: ENO=FALSE');
AssertTrue(Condition := F_S7EnoAddDint(diIn1 := 2147483646, diIn2 := 1), Message := 'ADD_D max - 1 + 1: ENO=TRUE');
AssertFalse(Condition := F_S7EnoSubDint(diIn1 := -2147483647 - 1, diIn2 := 1), Message := 'SUB_D min - 1: ENO=FALSE');
AssertFalse(Condition := F_S7EnoMulDint(diIn1 := 65536, diIn2 := 32768), Message := 'MUL_D 2^16 * 2^15: ENO=FALSE');
AssertTrue(Condition := F_S7EnoMulDint(diIn1 := 65536, diIn2 := 32767), Message := 'MUL_D 2^16 * 32767: ENO=TRUE');
coUnit.TEST_FINISHED();
