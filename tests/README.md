# Test Scripts

This directory contains test scripts for the Roulette Bot project.

## Test Files

- `test_*.py` - Various test scripts for different components
- `roulette_bot_test.py` - Main bot test script
- `*.ipynb` - Jupyter notebook test files

## Running Tests

### Unit Tests
```bash
pytest backend/tests/
```

### Integration Tests
```bash
python tests/test_bot_comprehensive.py
```

### Specific Component Tests
```bash
python tests/test_detection_pipeline.py
python tests/test_template_matching.py
```

## Note

Some test scripts may require specific setup or configuration. Refer to individual test files for requirements.

