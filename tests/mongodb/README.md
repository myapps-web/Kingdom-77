# MongoDB Tests
# =============

This directory contains test utilities for MongoDB integration.

## Test Files

### test_import.py
Quick test to verify MongoDB modules can be imported correctly.
```bash
python tests/mongodb/test_import.py
```

### test_mongodb.py
Comprehensive MongoDB connection test with database statistics.
```bash
python tests/mongodb/test_mongodb.py
```

### test_simple_connection.py
Simple direct connection test using motor driver.
```bash
python tests/mongodb/test_simple_connection.py
```

### test_db_update.py
Debug utility to verify global db variable updates correctly.
```bash
python tests/mongodb/test_db_update.py
```

## Usage

Run all tests to verify MongoDB setup:
```bash
# Test imports
python tests/mongodb/test_import.py

# Test connection
python tests/mongodb/test_mongodb.py
```

## Requirements

- MongoDB Atlas account configured
- MONGODB_URI in .env file
- Dependencies installed: motor, pymongo, dnspython
