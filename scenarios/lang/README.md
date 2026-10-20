# Сценарии корпуса всех языков (`scenarios/lang/`)

Сценарии поведения блоков SimaticML из `samples/lang/` — в том же формате CSV, что и сценарии корпуса
SCL ([../README.md](../README.md), раздел «Формат CSV»). Отдельный каталог нужен, чтобы инструменты,
которые обходят `scenarios/*.csv` (генератор тестов корпуса SCL, соседние проекты миграции), не
подхватили блоки другого корпуса.

**Откуда ожидаемые значения.** Их считают модели `reference/model_*.py`, написанные по описанию логики
блоков в [samples/lang/README.md](../../samples/lang/README.md) (тот же текст — в комментарии блока
SimaticML), а не по XML и не по результату конвертера. Вторая проверка — контрольные точки, посчитанные
вручную (`HAND_CHECKS` в `reference/test_lang_scenario_models.py`). Общая часть моделей (часы, таймеры,
запись CSV) — `../reference/scenario_lib.py`.

```bat
python scenarios/lang/reference/generate_lang_csv.py          # пересчитать CSV
python scenarios/lang/reference/generate_lang_csv.py --check  # сравнить с файлами (CI)
```

## Файлы

| CSV | Блоки | Сценариев | Вызовов | Таймеры | Что проверяет |
|---|---|---|---|---|---|
| [FB_Starter.csv](FB_Starter.csv) | `FB_StarterLad`, `FB_StarterFbd`, `FB_StarterStl`, `FB_StarterScl` | 9 | 47 | TON | пуск/стоп, Пуск и Стоп одновременно (SR S7: сброс главнее), блокировки, обратная связь в срок и с опозданием (на пороге), авария с самоподхватом и сброс, счётчик пусков по фронту |
| [FB_PumpInterlockLad.csv](FB_PumpInterlockLad.csv) | `FB_PumpInterlockLad` | 5 | 25 | нет | защёлка аварии по уровню и давлению, квитирование, прыжок мимо сетей при обслуживании (сеть 7 не выполняется — бит фронта и ENO сохраняют значения), ENO сложения, три вызова через EN/ENO |

## Алиасы

В CSV нет комментариев, поэтому соответствие «файл сценариев → блоки» лежит в
[aliases.json](aliases.json): один `FB_Starter.csv` проверяет все четыре перевода пускателя. Генератор
тестов делает по набору coUnit на каждый блок (`FB_StarterLad_ScenarioTest` …), `s7conv equiv` берёт
семейство из того же файла и сверяет перевод SCL с эталоном LAD.

## Где выполняются

- `python -m s7conv build-corpus` пишет наборы в `tests/POUs/ScenariosLang/` и объявляет их в `PRG_Tests`;
  `python tools/codesys/cds.py test` выполняет их в CODESYS Control Win вместе с наборами корпуса SCL.
- Интерпретатор ST (`s7conv/sim/stsim.py`) выполняет те же наборы в pytest
  (`s7conv/tests/test_scenarios_simulated.py`).
- `python -m s7conv equiv samples/lang --scenarios scenarios/lang` подаёт строки сценариев эталону S7 и
  переводу в stsim и сравнивает выходы и статику после каждого вызова.
