cmdTmp.start := GVL_IO.Start_PB;
cmdTmp.stop := NOT GVL_IO.Stop_PB;
cmdTmp.mode := 1;
GVL_InstanceDBs.Motor1_DB(cmd := cmdTmp, feedback := GVL_IO.I0_2, ack := DB_Hmi.ackRequest);
GVL_IO.Motor_Run := GVL_InstanceDBs.Motor1_DB.run;
GVL_InstanceDBs.Delay_DB(IN := GVL_InstanceDBs.Motor1_DB.fault, PT := T#10s);
GVL_IO.Horn := GVL_InstanceDBs.Delay_DB.Q;
GVL_Markers.MW10 := INT_TO_WORD(DB_Hmi.counter);
GVL_Markers.M12_1 := GVL_Markers.MW10.3;
