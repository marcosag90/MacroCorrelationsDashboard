# Macro Correlations

A Python project for analyzing correlations between Bitcoin and various macro assets.

## Setup

1. Clone the repository
2. Run the setup script to create a virtual environment and install dependencies:
   ```bash
   ./setup.sh
   ```
   
   Or manually:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Running the Application

```bash
streamlit run src/main.py
```

## Testing

### Running Tests Manually

To run tests manually from the command line:

```bash
# From the project root directory
python -m unittest discover -s tests

# Run with more detailed output
python -m unittest discover -s tests -v

# Run a specific test file
python -m unittest tests/test_correlation.py

# Run a specific test class
python -m unittest tests.test_correlation.TestCorrelation

# Run a specific test method
python -m unittest tests.test_correlation.TestCorrelation.test_normalize_series
```

**Note:** Running tests manually at least once often helps VS Code properly discover and recognize the tests in the Testing tab. If VS Code is not detecting tests, try running them manually first, then restart the VS Code Testing view.

## Project Structure

- `src/`: Main source code
  - `data_processing/`: Data processing modules
  - `datafeed/`: Data retrieval modules
  - `config/`: Configuration handling
  - `views/`: Streamlit UI views
- `tests/`: Unit tests