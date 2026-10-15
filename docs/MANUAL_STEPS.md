# Ручные шаги

Шаги, которые выполняет человек в IDE CODESYS или в консоли Windows. Всё, что можно выполнить без
CODESYS (сборка текстов, линтер, статанализ), описано в [README](../README.md#быстрый-старт-без-железа)
и выполняется в CI.

> Команды скриптов CODESYS в этом документе — **будет уточнено после прогона скриптов**.
> До первого реального прогона они не считаются проверенными.

## 1. Установка CODESYS 3.5.17.30 и CfUnit

1. Скачать CODESYS V3.5 SP17 Patch 3 (3.5.17.30) с сайта ОВЕН (раздел ПО для ПЛК2xx) и установить
   с компонентом CODESYS Control Win V3.
2. Установить пакет таргет-файлов ОВЕН ПЛК210: «Инструменты → Установщик пакетов» (Tools → Package
   Manager). Версию таргет-файла сверить с прошивкой ПЛК.
3. Установить CfUnit 1.2.0.0 — в этой версии библиотека называется co♻e / coUnit, пространство
   имён в коде `coUnit` (см. [ASSUMPTIONS.md](ASSUMPTIONS.md), C6). Источник — SVN проекта counit
   на CODESYS Forge (`tags/v1.2.0.0/`): пакет `v1.2.0.0.package` ставится через CODESYS
   Installer, либо сама библиотека `co♻e.library` — через «Инструменты → Репозиторий библиотек
   → Установить» (Tools → Library Repository → Install). Проверка ссылки запросом `HEAD` даёт
   401 — скачивать обычным `GET` (браузером).
4. Добавить библиотеку в Library Manager тестового приложения и уменьшить её параметры
   (`GVL_Param_coUnit`): `MaxNumberOfTestSuites` 10–20, `MaxNumberOfTestsForEachTestSuite`
   ≤ 50, `MaxNumberOfAssertsForEachTestSuite` ≤ 200. С параметрами по умолчанию сборка падает
   с C0106 (нехватка глобальной памяти, около 78 МБ). Где это редактируется в SP17 Patch 3 —
   будет уточнено при установке (пункт C7 в ASSUMPTIONS.md).
5. Записать установленную версию в [TEST_REPORT.md](TEST_REPORT.md).
6. Проверить запуск из консоли: `"%CODESYS_EXE%" --help` — сохранить вывод в
   `build/codesys_help.txt` (в git не попадает): по нему уточняются ключи `--profile`, `--noUI`,
   `--runscript`.

## 2. Переменные окружения CODESYS_EXE и CODESYS_PROFILE

Скрипты и инструменты берут путь к CODESYS только из переменных окружения — абсолютных путей
в репозитории нет.

| Переменная | Значение | Пример (сверить со своей установкой) |
|---|---|---|
| `CODESYS_EXE` | полный путь к `CODESYS.exe` | `C:\Program Files\CODESYS 3.5.17.30\CODESYS\Common\CODESYS.exe` |
| `CODESYS_PROFILE` | имя профиля установки | `CODESYS V3.5 SP17 Patch 3` |

Задать для пользователя (PowerShell, затем перезапустить консоль):

```powershell
[Environment]::SetEnvironmentVariable("CODESYS_EXE", "<путь к CODESYS.exe>", "User")
[Environment]::SetEnvironmentVariable("CODESYS_PROFILE", "<имя профиля>", "User")
```

Имя профиля видно в заголовке окна CODESYS и в каталоге `Profiles` установки.

## 3. Импорт исходников в проект

Скрипт `tools/codesys/import_sources.py` создаёт или пересоздаёт объекты проекта из `src/`
(с флагом тестов — и из `tests/`, в папку `Tests`), сохраняет проект, лог пишет в `build/import.log`.

```bat
rem будет уточнено после прогона скриптов
"%CODESYS_EXE%" --profile="%CODESYS_PROFILE%" --noUI --runscript="tools\codesys\import_sources.py"
```

Что создаётся только руками (не входит в раскладку, см. [LAYOUT.md](LAYOUT.md#чего-в-раскладке-нет-ручные-шаги)):

- [ ] дерево устройств: ПЛК210 для рабочей сборки, CODESYS Control Win V3 для тестов;
- [ ] конфигурация задач, если скрипт не смог создать её по `tools/codesys/config.json`;
- [ ] визуализации, конфигураторы обмена, графические языки.

## 4. Сборка

```bat
rem будет уточнено после прогона скриптов
"%CODESYS_EXE%" --profile="%CODESYS_PROFILE%" --noUI --runscript="tools\codesys\build.py"
```

Сообщения компилятора — в `build/build.log`. Если сборка в IDE даёт ошибки, которых нет в логе,
скопируйте их в [BUILD_ERRORS.md](BUILD_ERRORS.md).

## 5. Запуск тестов

1. Запустить рантайм: значок CODESYS Control Win V3 в трее → Start PLC.
2. Запустить скрипт тестов:

   ```bat
   rem будет уточнено после прогона скриптов
   "%CODESYS_EXE%" --profile="%CODESYS_PROFILE%" --noUI --runscript="tools\codesys\run_tests.py"
   ```

3. Вручную (если скрипт недоступен): импорт с тестами → «Онлайн → Логин» → «Старт» →
   дождаться `PRG_Tests.xAllFinished = TRUE` → результаты в журнале устройства (Device → Log,
   логгер `coUnit` или `co♻e`). Итоговый блок `TESTS FINISHED RUNNING` coUnit пишет с классом
   ERROR даже при зелёном прогоне — смотреть на счётчик `Failed tests`.
4. XML с результатами (xUnit) рантайм может записать не по пути из параметров библиотеки, а в
   каталог `PlcLogic` рабочей папки Control Win — будет уточнено после прогона скриптов.
5. Перенести итог в [TEST_REPORT.md](TEST_REPORT.md): версия CODESYS и coUnit, число тестов,
   упавшие тесты с сообщениями.

Без лицензии Control Win работает 2 часа, потом его нужно перезапустить.

## 6. Экспорт перед коммитом

Если что-то правилось в IDE, перед коммитом выгрузите объекты обратно в `src/` и проверьте дифф:

```bat
rem будет уточнено после прогона скриптов
"%CODESYS_EXE%" --profile="%CODESYS_PROFILE%" --noUI --runscript="tools\codesys\export_sources.py"
git diff --stat
```

Цикл «импорт → экспорт» без правок в IDE не должен давать диффа. Если дифф есть — это ошибка
скриптов, её нужно записать в issue.

## 7. Зеркало на GitVerse или GitFlic

1. Создать пустой репозиторий на GitVerse или GitFlic (без README и лицензии).
2. Добавить его как второй remote и отправить все ветки и теги:

   ```bash
   git remote add mirror <url-зеркала>
   git push mirror --all
   git push mirror --tags
   ```

3. После каждого релиза повторять `git push mirror --all` и `git push mirror --tags`.
