coUnit.TEST('AddIntOverflow');
AssertFalse(Condition := F_S7EnoAddInt(iIn1 := 32767, iIn2 := 1), Message := 'ADD_I 32767 + 1: overflow, ENO=FALSE');
AssertTrue(Condition := F_S7EnoAddInt(iIn1 := 32766, iIn2 := 1), Message := 'ADD_I 32766 + 1: ENO=TRUE');
AssertTrue(Condition := F_S7EnoAddInt(iIn1 := -32768, iIn2 := 0), Message := 'ADD_I -32768 + 0: ENO=TRUE');
coUnit.TEST_FINISHED();
