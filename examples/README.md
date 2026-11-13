# Примеры использования `apk-dep-graph`

В этом каталоге собраны готовые конфигурации и описания графов,
демонстрирующие все режимы работы утилиты. Каждый пример можно
запустить напрямую из корня репозитория.

## Оглавление

- [Пример 1. Реальный репозиторий Alpine](#пример-1-реальный-репозиторий-alpine)
- [Пример 2. Обратные зависимости](#пример-2-обратные-зависимости)
- [Пример 3. Тестовый режим: простой граф](#пример-3-тестовый-режим-простой-граф)
- [Пример 4. Тестовый режим: граф с циклом](#пример-4-тестовый-режим-граф-с-циклом)
- [Пример 5. Тестовый режим: глубокий граф](#пример-5-тестовый-режим-глубокий-граф)
- [Пример 6. Ограничение глубины](#пример-6-ограничение-глубины)
- [Сводная таблица примеров](#сводная-таблица-примеров)

## Пример 1. Реальный репозиторий Alpine

Демонстрирует работу с настоящим `APKINDEX.tar.gz` из официального
репозитория Alpine Linux.

**Файл `musl.csv`:**

```csv
package,musl
repository,https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64
test_mode,false
package_version,1.2.5-r0
output_image,musl.svg
ascii_tree,true
max_depth,3
```

**Запуск:**

```bash
./run.sh --config examples/musl.csv
```

**Что должно произойти:**

1. Выведутся все параметры конфигурации в формате `ключ=значение`.
2. Скачается `APKINDEX.tar.gz` по указанному URL.
3. Найдётся запись пакета `musl` версии `1.2.5-r0`.
4. Напечатается граф зависимостей до глубины 3.
5. Сохранится файл `musl.svg` с изображением графа (PlantUML).
6. В консоль выведется ASCII-дерево зависимостей.

**Ожидаемый фрагмент вывода:**

```
== Конфигурация ==
package=musl
repository=https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64
test_mode=False
package_version=1.2.5-r0
output_image=musl.svg
ascii_tree=True
max_depth=3

== Граф зависимостей ==
musl: so:libc.musl-x86_64.so.1
...
```

> **Замечание.** Точный список зависимостей зависит от версии
> Alpine и содержимого APKINDEX на момент запуска.

## Пример 2. Обратные зависимости

Демонстрирует флаг `--reverse`, который выводит пакеты, зависящие
от заданного.

**Запуск** (использует конфигурацию из примера 1):

```bash
./run.sh --config examples/musl.csv --reverse musl
```

**Что должно произойти дополнительно:**

После вывода графа зависимостей появится секция:

```
== Обратные зависимости musl ==
musl
...
```

Будут перечислены все пакеты из APKINDEX, которые (транзитивно)
зависят от `musl`. Поскольку в индексе тысячи пакетов, список может
быть большим — для наглядности уменьшите `max_depth` до 1 или 2.

## Пример 3. Тестовый режим: простой граф

Демонстрирует тестовый режим без обращения к сети.

**Файл `examples/test_simple.csv`:**

```csv
package,A
repository,tests/fixtures/simple_graph.txt
test_mode,true
package_version,1.0
output_image,test_simple.svg
ascii_tree,true
max_depth,5
```

**Файл `tests/fixtures/simple_graph.txt`:**

```
A B
A C
B D
C D
D E
```

**Запуск:**

```bash
./run.sh --config examples/test_simple.csv
```

**Ожидаемый вывод:**

```
== Конфигурация ==
package=A
repository=tests/fixtures/simple_graph.txt
test_mode=True
package_version=1.0
output_image=test_simple.svg
ascii_tree=True
max_depth=5

== Граф зависимостей ==
A: B, C
B: D
C: D
D: E
E: -

SVG сохранён в test_simple.svg
== ASCII-дерево ==
A
├── B
│   └── D
│       └── E
└── C
    └── D
        └── E
```

## Пример 4. Тестовый режим: граф с циклом

Демонстрирует корректную обработку циклических зависимостей.

**Файл `examples/test_cycle.csv`:**

```csv
package,A
repository,tests/fixtures/cycle_graph.txt
test_mode,true
package_version,1.0
output_image,test_cycle.svg
ascii_tree,true
max_depth,10
```

**Файл `tests/fixtures/cycle_graph.txt`:**

```
A B
B C
C A
C D
```

**Запуск:**

```bash
./run.sh --config examples/test_cycle.csv
```

**Ожидаемый вывод:**

```
== Граф зависимостей ==
A: B
B: C
C: A, D
D: -
```

Обход завершается, несмотря на цикл `A → B → C → A`, потому что
каждый узел попадает в результат только на минимальной глубине.

## Пример 5. Тестовый режим: глубокий граф

Демонстрирует работу при большой глубине.

**Файл `examples/test_deep.csv`:**

```csv
package,A
repository,tests/fixtures/deep_graph.txt
test_mode,true
package_version,1.0
output_image,test_deep.svg
ascii_tree,true
max_depth,10
```

**Файл `tests/fixtures/deep_graph.txt`:**

```
A B
B C
C D
D E
E F
```

**Запуск:**

```bash
./run.sh --config examples/test_deep.csv
```

**Ожидаемый граф:**

```
A: B
B: C
C: D
D: E
E: F
F: -
```

## Пример 6. Ограничение глубины

Демонстрирует влияние параметра `max_depth` на результат.

Используем тот же `deep_graph.txt`, но с `max_depth = 2`.

**Файл `examples/test_depth.csv`:**

```csv
package,A
repository,tests/fixtures/deep_graph.txt
test_mode,true
package_version,1.0
output_image,test_depth.svg
ascii_tree,false
max_depth,2
```

**Запуск:**

```bash
./run.sh --config examples/test_depth.csv
```

**Ожидаемый вывод:**

```
== Граф зависимостей ==
A: B
B: C
```

Узлы `D`, `E`, `F` не попадают в результат, потому что находятся
глубже `max_depth = 2`. Секция ASCII-дерева отсутствует, так как
`ascii_tree = false`.

## Сводная таблица примеров

| Пример | Файл конфигурации            | Режим    | Что показывает                                |
|--------|------------------------------|----------|-----------------------------------------------|
| 1      | `musl.csv`                   | реальный | загрузка APKINDEX и полный граф зависимостей  |
| 2      | `musl.csv` + `--reverse`     | реальный | обратные зависимости                          |
| 3      | `test_simple.csv`            | тестовый | базовый граф и ASCII-дерево                   |
| 4      | `test_cycle.csv`             | тестовый | обработка циклов                              |
| 5      | `test_deep.csv`              | тестовый | глубокая цепочка зависимостей                 |
| 6      | `test_depth.csv`             | тестовый | ограничение глубины                           |

## Добавление собственного примера

1. Создайте CSV-файл с обязательными ключами
   `package`, `repository`, `package_version`.
2. Для тестового режима создайте файл описания графа
   (по одному ребру `A B` на строку) и укажите путь к нему
   в `repository`.
3. Запустите:

   ```bash
   ./run.sh --config examples/your_example.csv
   ```