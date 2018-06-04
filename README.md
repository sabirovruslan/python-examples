## Анализатор логов

Для запуска через makefile требуется установленный docker

Команды make необходимо выполнять из корневой директории проекта

### Запуск Unit тестов

```
make unit-test
```

### Запуск анализатора

```
make log-analyzer
```

### Запуск анализатора с переопределенным конфигом

```
make log-analyzer-config
```

### Ручной запуск анализатора

```
python3 log_analyzer.py
```

или 

```
python log_analyzer.py --config ./config.cfg
```
