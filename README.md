# DICOM Attribute Extractor
This tool is used to extract specific attributes from DICOM images.
The attributes are saved as `.json`.

## How to install

1. Install python on your PC. [Link](https://www.python.org/)
2. Install pip (should be installed with python installer)
3. Install poetry
```sh
$ pip install poetry
```
4. Install poetry environment
```sh
$ poetry install
```
5. Run the script
```sh
$ poetry run python main.py --help                                                                master!?
Usage: main.py [OPTIONS]

Options:
  -i, --input-folder DIRECTORY    Input folder which contains images to
                                  extract the attribute from.  [default:
                                  ./input_data]
  -l, --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set logging level.  [default: INFO]
  -o, --output-file TEXT          Output file name  [default:
                                  results-2024-05-20_15-28-26.json]
  -a, --attribute HEXADECIMAL     Which attributes to extract from DICOM
                                  images  [required]
  --help                          Show this message and exit.
```

## Notes

- Debug level can be set using env variable, e.g., `export LOG_LEVEL=INFO`
- Attributes are specified using hex numbers