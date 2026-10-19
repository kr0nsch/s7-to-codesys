// AUTO-GENERATED — не редактировать: s7conv gen-tests
// Все зарегистрированные наборы выполняются параллельно; итоги — в журнал устройства (логгер
// coUnit) и в XML-файл xUnit.
coUnit.RUN();

// AreAllTestsFinished() вызывается после RUN(): у метода есть побочный эффект на первом цикле.
// Наборы объединяются через AND (не AND_THEN): метод вызывается у каждого набора в каждом цикле.
xAllFinished := fbF_NormXTest.AreAllTestsFinished()
        AND fbF_S7NowTest.AreAllTestsFinished()
        AND fbF_ScaleXTest.AreAllTestsFinished()
        AND fbS7FTrigTest.AreAllTestsFinished()
        AND fbS7TofTest.AreAllTestsFinished()
        AND fbS7TonTest.AreAllTestsFinished()
        AND fbS7TpTest.AreAllTestsFinished()
        AND fbStandardCounterTest.AreAllTestsFinished()
        AND fbAlarmDelay_ScenarioTest.AreAllTestsFinished()
        AND fbAnalogIn_ScenarioTest.AreAllTestsFinished()
        AND fbMotor_ScenarioTest.AreAllTestsFinished()
        AND fbPumpAlternation_ScenarioTest.AreAllTestsFinished()
        AND fbSequencer_ScenarioTest.AreAllTestsFinished()
        AND fbTotalizer_ScenarioTest.AreAllTestsFinished();
