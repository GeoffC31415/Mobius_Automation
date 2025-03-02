# Reptile Vivarium Monitoring System

A Python-based system for monitoring and controlling a reptile vivarium environment including temperature, humidity, lighting, and file management.

## Proposed Structure

```
mobius/
├── __init__.py
├── config/
│   ├── __init__.py
│   ├── settings.py         # All settings in one place
│   └── secrets.py          # Handles secrets management
├── core/
│   ├── __init__.py
│   ├── controller.py       # Main controller class
│   └── scheduler.py        # Handles timing of various operations
├── hardware/
│   ├── __init__.py
│   ├── relay.py            # Relay control
│   ├── sensor.py           # Sensor abstractions
│   └── drivers/
│       ├── __init__.py
│       ├── dht.py          # DHT sensor driver
│       └── onewire.py      # One-wire temperature sensor driver
├── services/
│   ├── __init__.py
│   ├── influx_client.py    # InfluxDB interface
│   ├── file_manager.py     # File management functionality
│   └── logging.py          # Logging service
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Helper functions
└── main.py                 # Application entry point
```

## Key Design Improvements

1. **Object-Oriented Approach**: Structured as classes with single responsibilities
2. **Configuration Management**: Centralized settings and secrets
3. **Separation of Concerns**: Hardware, services, and business logic separated
4. **Dependency Injection**: Components receive dependencies rather than importing globally
5. **Error Handling**: Improved error handling and recovery
6. **Testability**: Structure facilitates unit testing
7. **Extensibility**: Easy to add new sensors and devices

## Transition Plan

1. Create the new structure with minimal functionality
2. Migrate core functions one at a time
3. Add comprehensive error handling
4. Write tests for critical components
5. Gradually phase out the old code
