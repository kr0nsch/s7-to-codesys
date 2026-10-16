norm := F_NormX(rMin := 0, rValue := raw, rMax := RAW_MAX);
valid := raw >= -864 AND raw <= 28512;
FC_ScaleAnalog := F_ScaleX(rMin := low, rValue := norm, rMax := high);
