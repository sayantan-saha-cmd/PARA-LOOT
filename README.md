# Paraloot

Paraloot is a combined URL parameter discovery and fuzzing tool that integrates crawling and Wayback Machine URL mining techniques. It helps security researchers and penetration testers discover URL parameters for a given domain, clean and fuzz them to identify potential vulnerabilities.

## Features

- Fetches URLs related to a target domain from the Wayback Machine.
- Cleans URLs by removing unnecessary extensions and normalizing query parameters.
- Crawls the target domain to discover additional URL parameters.
- Generates fuzzed URLs by replacing parameter values with a placeholder (default: `FUZZ`).
- Supports optional proxy usage for web requests.
- Saves all discovered URLs, parameters, and fuzzed URLs progressively to an output file.
- Interactive CLI with prompts for domain and output filename.
- Displays a logo and author information on startup.

## Installation

1. Ensure you have Python 3.6 or higher installed.
2. Install required Python packages:

```bash
pip install requests beautifulsoup4
```

3. Download or clone the repository containing `paraloot.py`.

## Usage

Run the tool using Python:

```bash
git clone https://github.com/sayantan-saha-cmd/PARA-LOOT.git
cd PARA-LOOT
pip install -r requirements.txt
python paraloot.py
```

You will be prompted to enter:

- **Domain Name:** The target domain to discover URL parameters for (e.g., `example.com`).
- **File Name:** The output filename where results will be saved.

Alternatively, you can provide command line arguments:

```bash
python paraloot.py -d example.com -l output.txt
```

## Output

The output file will contain:

- Cleaned URLs with parameters fetched from the Wayback Machine.
- Additional parameters discovered via crawling.
- Fuzzed URLs with parameter values replaced by the placeholder.

## Author

Sayantan Saha  
- LinkedIn: [https://www.linkedin.com/in/mastersayantan/](https://www.linkedin.com/in/mastersayantan/)  
- GitHub: [https://github.com/MasterSayantan](https://github.com/MasterSayantan)

## License

This project is licensed under the MIT License.
