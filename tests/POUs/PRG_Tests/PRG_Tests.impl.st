// AUTO-GENERATED — не редактировать: s7conv gen-tests
// Все зарегистрированные наборы выполняются параллельно; итоги — в журнал устройства (логгер
// coUnit) и в XML-файл xUnit.
coUnit.RUN();

// AreAllTestsFinished() вызывается после RUN(): у метода есть побочный эффект на первом цикле.
// Наборы объединяются через AND (не AND_THEN): метод вызывается у каждого набора в каждом цикле.
xAllFinished := fbBackwashGraph_SeqTest.AreAllTestsFinished()
        AND fbF_NormXTest.AreAllTestsFinished()
        AND fbF_S7EnoTest.AreAllTestsFinished()
        AND fbF_S7NowTest.AreAllTestsFinished()
        AND fbF_ScaleXTest.AreAllTestsFinished()
        AND fbS5CounterTest.AreAllTestsFinished()
        AND fbS5TimerTest.AreAllTestsFinished()
        AND fbS7FTrigTest.AreAllTestsFinished()
        AND fbS7TofTest.AreAllTestsFinished()
        AND fbS7TonTest.AreAllTestsFinished()
        AND fbS7TpTest.AreAllTestsFinished()
        AND fbStandardCounterTest.AreAllTestsFinished()
        AND fbStandardFlipFlopTest.AreAllTestsFinished()
        AND fbBackwashGraph_ScenarioTest.AreAllTestsFinished()
        AND fbConveyorStl_ScenarioTest.AreAllTestsFinished()
        AND fbPumpInterlockLad_ScenarioTest.AreAllTestsFinished()
        AND fbStarterFbd_ScenarioTest.AreAllTestsFinished()
        AND fbStarterLad_ScenarioTest.AreAllTestsFinished()
        AND fbStarterScl_ScenarioTest.AreAllTestsFinished()
        AND fbStarterStl_ScenarioTest.AreAllTestsFinished()
        AND fbAlarmDelay_ScenarioTest.AreAllTestsFinished()
        AND fbAnalogIn_ScenarioTest.AreAllTestsFinished()
        AND fbMotor_ScenarioTest.AreAllTestsFinished()
        AND fbPumpAlternation_ScenarioTest.AreAllTestsFinished()
        AND fbSequencer_ScenarioTest.AreAllTestsFinished()
        AND fbTotalizer_ScenarioTest.AreAllTestsFinished();
