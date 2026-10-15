# Отчёт о тестировании

Результаты юнит-тестов CfUnit (coUnit 1.2.0.0) в CODESYS Control Win V3 и проверок без CODESYS.
Запись «проверено в CODESYS» появляется только после реального прогона.

## Окружение прогона

| Параметр | Значение |
|---|---|
| Дата прогона | — |
| Коммит | — |
| CODESYS | 3.5.17.30 (V3.5 SP17 Patch 3) — _не запускалось_ |
| Рантайм | CODESYS Control Win V3 — _не запускалось_ |
| CfUnit (coUnit) | 1.2.0.0 — _не установлена_ |
| Способ запуска | `tools/codesys/run_tests.py` / вручную по [MANUAL_STEPS.md](MANUAL_STEPS.md#5-запуск-тестов) |

## Сводка

| Набор | Тестов | Пройдено | Упало | Итог |
|---|---|---|---|---|
| `FB_F_Clamp_Test` | 7 | — | — | не запускалось |
| `FB_Example_Test` | 11 | — | — | не запускалось |

## Тесты

| Набор | Тест | Что проверяет | Итог |
|---|---|---|---|
| `FB_F_Clamp_Test` | `InsideRangeReturnsValue` | значение внутри диапазона не меняется | — |
| `FB_F_Clamp_Test` | `BelowLowReturnsLow` | значение ниже диапазона → нижняя граница | — |
| `FB_F_Clamp_Test` | `AboveHighReturnsHigh` | значение выше диапазона → верхняя граница | — |
| `FB_F_Clamp_Test` | `AtLowBoundaryReturnsLow` | значение на нижней границе не меняется | — |
| `FB_F_Clamp_Test` | `AtHighBoundaryReturnsHigh` | значение на верхней границе не меняется | — |
| `FB_F_Clamp_Test` | `EqualBoundsReturnsBound` | вырожденный диапазон `rLow = rHigh` | — |
| `FB_F_Clamp_Test` | `LowGreaterThanHighSwapsBounds` | `rLow > rHigh`: границы меняются местами | — |
| `FB_Example_Test` | `AutoSwitchesOnBelowThreshold` | авторежим: значение ниже порога включения (уставка − гистерезис) включает выход, отказа нет | — |
| `FB_Example_Test` | `AutoThresholdsAreInclusive` | авторежим: на пороге включения выход включается, на уставке — отключается | — |
| `FB_Example_Test` | `AutoHoldsStateInsideHysteresis` | авторежим: в зоне гистерезиса выход сохраняет состояние (после включения и после отключения) | — |
| `FB_Example_Test` | `InvalidValueLatchesFault` | недостоверное измерение в авторежиме: отказ, выход отключён; отказ держится после восстановления измерения | — |
| `FB_Example_Test` | `AcknowledgeClearsFaultWhenValid` | `Acknowledge()` при достоверном измерении снимает отказ и возвращает TRUE, выход снова управляется | — |
| `FB_Example_Test` | `AcknowledgeKeepsFaultWhileInvalid` | `Acknowledge()` при недостоверном измерении возвращает FALSE, отказ остаётся | — |
| `FB_Example_Test` | `ManualFollowsCommand` | ручной режим: выход повторяет `xManualOn`, недостоверное измерение отказа не даёт | — |
| `FB_Example_Test` | `LocalAndOutOfServiceSwitchOff` | `Local` и `OutOfService` отключают выход при любых измерении и команде | — |
| `FB_Example_Test` | `DefaultModeIsOutOfService` | режим по умолчанию — `OutOfService`: выход отключён | — |
| `FB_Example_Test` | `ParametersAreClamped` | уставка и гистерезис вне диапазона ограничиваются `EXAMPLE_SP_MAX_PCT` и `EXAMPLE_HYST_MIN_PCT` | — |
| `FB_Example_Test` | `CountsSwitchOnsAndResetClears` | счётчик `Count` считает только фронты включения; `Reset()` через `I_Resettable` отключает выход и обнуляет счётчик | — |

## Упавшие тесты

_Нет данных._ Формат: набор, тест, сообщение CfUnit (Expected / Actual), причина, исправление.

## Проверки без CODESYS

Итоги последнего прогона CI (ссылка на запуск GitHub Actions) или локального прогона.

| Проверка | Итог | Примечание |
|---|---|---|
| `ruff check`, `ruff format --check`, `mypy`, `pytest` | пройдено, 2026-10-16, локально | pytest: все тесты, включая интеграционные с настоящими `plc` и iec_checker |
| `tools/assemble.py` (все варианты, с `--tests` и без) | пройдено, 2026-10-16, локально | 8 объектов `src/` + 3 объекта `tests/` |
| `tools/check/st_lint.py --strict` | пройдено, 2026-10-16, локально | 60 файлов, 0 замечаний |
| iec_checker 0.4 (локально, `run_iec_checker.py --tests`) | пройдено, 2026-10-16 | 11 файлов, ошибок разбора нет; необоснованных находок 0, обоснованных 100 — разбор в [STATIC_ANALYSIS.md](STATIC_ANALYSIS.md) |
| RuSTy 1.0.6 (локально, `run_rusty.py`) | пройдено, 2026-10-16 | 11 файлов (`src/` и `tests/` с прокладкой coUnit), исключений нет, 0 ошибок, 0 предупреждений |
