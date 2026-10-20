// AUTO-GENERATED — не редактировать: s7conv gen-tests — список наборов собирается из tests/ (рукописные наборы
//             EXTENDS coUnit.FB_TestSuite) и сценариев scenarios/*.csv; новый набор — пересоздать.
// Назначение: программа запуска юнит-тестов CfUnit (coUnit 1.2.0.0). Объявляет экземпляры наборов
//             тестов (объявление регистрирует набор в coUnit) и каждый цикл вызывает coUnit.RUN().
//             Назначается задаче только тестового приложения (CODESYS Control Win), не рабочего ПЛК.
// Автор:      s7conv 0.1.0 (сгенерировано)
// Версия:     не указана
// Документ:   docs/TEST_REPORT.md, docs/methodology.md
PROGRAM PRG_Tests
VAR
    fbF_NormXTest : FB_F_NormX_Test;  // рукописный набор
    fbF_S7EnoTest : FB_F_S7Eno_Test;  // рукописный набор
    fbF_S7NowTest : FB_F_S7Now_Test;  // рукописный набор
    fbF_ScaleXTest : FB_F_ScaleX_Test;  // рукописный набор
    fbS7FTrigTest : FB_S7FTrig_Test;  // рукописный набор
    fbS7TofTest : FB_S7Tof_Test;  // рукописный набор
    fbS7TonTest : FB_S7Ton_Test;  // рукописный набор
    fbS7TpTest : FB_S7Tp_Test;  // рукописный набор
    fbStandardCounterTest : FB_StandardCounter_Test;  // рукописный набор
    fbStandardFlipFlopTest : FB_StandardFlipFlop_Test;  // рукописный набор
    fbPumpInterlockLad_ScenarioTest : FB_PumpInterlockLad_ScenarioTest;  // сценарии CSV всех языков (сгенерировано)
    fbStarterFbd_ScenarioTest : FB_StarterFbd_ScenarioTest;  // сценарии CSV всех языков (сгенерировано)
    fbStarterLad_ScenarioTest : FB_StarterLad_ScenarioTest;  // сценарии CSV всех языков (сгенерировано)
    fbStarterScl_ScenarioTest : FB_StarterScl_ScenarioTest;  // сценарии CSV всех языков (сгенерировано)
    fbStarterStl_ScenarioTest : FB_StarterStl_ScenarioTest;  // сценарии CSV всех языков (сгенерировано)
    fbAlarmDelay_ScenarioTest : FB_AlarmDelay_ScenarioTest;  // сценарии CSV (сгенерировано)
    fbAnalogIn_ScenarioTest : FB_AnalogIn_ScenarioTest;  // сценарии CSV (сгенерировано)
    fbMotor_ScenarioTest : FB_Motor_ScenarioTest;  // сценарии CSV (сгенерировано)
    fbPumpAlternation_ScenarioTest : FB_PumpAlternation_ScenarioTest;  // сценарии CSV (сгенерировано)
    fbSequencer_ScenarioTest : FB_Sequencer_ScenarioTest;  // сценарии CSV (сгенерировано)
    fbTotalizer_ScenarioTest : FB_Totalizer_ScenarioTest;  // сценарии CSV (сгенерировано)
    // все наборы завершены — флаг для скрипта запуска тестов (read_value)
    xAllFinished : BOOL;
END_VAR
