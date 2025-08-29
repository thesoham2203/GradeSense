# Sample Marksheets for Testing

This directory contains sample marksheets for testing the GradeSense API.

## Sample Files Description

### sample_marksheet_1.txt

Text representation of a CBSE Class 12 marksheet with:

- Student: Rahul Kumar
- Roll No: 1234567
- Registration: 12345678901
- Subjects: Physics, Chemistry, Mathematics, English, Computer Science
- Overall: First Division (78.2%)

### sample_marksheet_2.txt

Text representation of a University marksheet with:

- Student: Priya Sharma
- Roll No: CSE/18/001
- Semester: 8th Semester B.Tech
- CGPA: 8.45
- Subjects with credits and grades

### sample_marksheet_3.txt

Text representation of a State Board marksheet with:

- Student: Amit Singh
- Roll No: SB2023001
- Class: 10th Standard
- Percentage: 85.6%
- Multiple subjects with grades

## Usage

1. Place actual image or PDF marksheets in this directory
2. Run the test script: `python test_api.py`
3. The API will process these files and return structured JSON

## Creating Test Files

For testing purposes, you can:

1. Create simple text files with marksheet content
2. Use image editing software to create mockup marksheets
3. Scan or photograph real marksheets (ensure privacy compliance)

Note: The API works best with clear, high-resolution images or PDFs.
