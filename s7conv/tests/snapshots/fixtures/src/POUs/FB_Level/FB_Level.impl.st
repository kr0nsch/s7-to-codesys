level := FC_ScaleAnalog(raw := GVL_IO.Level_Raw,
                        low := DB_Settings.levelLow,
                        high := DB_Settings.levelHigh,
                        valid => sensorOk);
// MIGRATION-CHECK: SCALE_X с целым OUT: REAL_TO_INT округляет — сверить с S7 (стр. 66)
levelPercent := REAL_TO_INT(F_ScaleX(rMin := 0, rValue := level / 100.0, rMax := 100));
DB_Settings.totalVolume := DB_Settings.totalVolume + level * 0.001;
GVL_IO.Q4_0 := sensorOk AND level > DB_Settings.levelHigh;
// MIGRATION-CHECK: символ "Alarm_Lamp" не найден в корпусе и таблице тегов — объявлен в GVL_Tags (стр. 69)
GVL_Tags.Alarm_Lamp := NOT sensorOk;
