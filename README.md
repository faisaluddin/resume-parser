# Resume Parser

This is a simple resume parser that uses Spacy to extract information from resumes.

## Features

- Extracts personal information such as name, email, phone number, etc.
- Extracts education information such as degree, major, institution, etc.
- Extracts work experience information such as job title, company, duration, etc.
- Extracts skills information such as programming languages, frameworks, tools, etc.
- Outputs the extracted information in JSON format.

## Requirements

- Python 3.6 or higher
- Spacy 3.0 or higher
- PyPDF2 1.26 or higher

## Installation

- `git clone https://github.com/faisaluddin/resume-parser.git`
- `cd resume-parser`
- `bash python -m venv venv`
- `bash venv/Scripts/activate`
- `pip install -r requirements.txt`
- `python -m spacy download en_core_web_sm`
- `python -m nltk.downloader words`
- `python -m nltk.downloader stopwords`

## Usage

- `python -m resparser.main`

## Output

The script will create a output.json with the details

## License

This project is licensed under the MIT License - see the LICENSE file for details.
