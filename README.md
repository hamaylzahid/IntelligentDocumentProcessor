<!-- ============================================================ -->
<!-- Intelligent Document Understanding System - README.md -->
<!-- ============================================================ -->

<br>
<h1 align="center">Intelligent Document Understanding System</h1>
<br>

<p align="center">
AI-powered platform for automatic document analysis, extracting structured text, tables, contacts, and summaries from PDFs & images with unmatched speed and accuracy.
<p>
<br>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/OpenCV-4.8-green?style=for-the-badge&logo=opencv" alt="OpenCV">
  <img src="https://img.shields.io/badge/Tesseract-OCR-orange?style=for-the-badge" alt="Tesseract OCR">
  <img src="https://img.shields.io/badge/EasyOCR-red?style=for-the-badge" alt="EasyOCR">
  <img src="https://img.shields.io/badge/Camelot-PDF-yellow?style=for-the-badge" alt="Camelot">
  <img src="https://img.shields.io/badge/Gradio-UI-purple?style=for-the-badge" alt="Gradio">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="MIT License">
</p>

<hr>
<img src="media/demo.gif" alt="Demo of Intelligent Document Understanding System" width="600">

<br>
<h2 align="center">Table of Contents</h2>
<br>
<ul>
  <li><a href="#about-the-project">About the Project</a></li>
  <li><a href="#features">Features</a></li>
  <li><a href="#models-and-technologies-used">Models & Technologies Used</a></li>
  <li><a href="#installation">Installation</a></li>
  <li><a href="#usage">Usage</a></li>
  <li><a href="#project-architecture">Project Architecture</a></li>
  <li><a href="#contact">Contact</a></li>
  <li><a href="#license">License</a></li>
</ul>

<hr>

<br>
<h2 align="center">About the Project</h2>
<br>

<p>
The <strong>Intelligent Document Understanding System</strong> is a state-of-the-art AI-powered platform for automatic document analysis. It efficiently processes <strong>PDFs and images</strong>, extracts structured text, headings, key-value pairs, tables, and contact information, and generates a keyword-driven summary. 
Designed to be <strong>fast, accurate, and CPU-friendly</strong>, it combines classical OCR with deep learning-based techniques for robust performance in real-world document layouts.
</p>

<hr>

<br>
<h2 align="center">Features</h2>
<br>

<ul>
  <li>Automatic OCR extraction from PDFs and images.</li>
  <li>Fallback from Tesseract OCR to EasyOCR for high accuracy.</li>
  <li>Minimal preprocessing for speed; adaptive preprocessing for complex layouts.</li>
  <li>Text structuring including paragraphs, headings, and key-value detection.</li>
  <li>Contact extraction: emails, phone numbers, URLs.</li>
  <li>Table extraction from PDFs using Camelot.</li>
  <li>Keyword-driven document summarization and abstract generation.</li>
  <li>Interactive Gradio UI for fast, real-time document analysis.</li>
  <li>JSON output suitable for integration with other applications.</li>
</ul>

<hr>

<br>
<h2 align="center">Models & Technologies Used</h2>
<br>

<ul>
  <li><strong>Tesseract OCR:</strong> CPU-efficient OCR engine for fast text extraction.</li>
  <li><strong>EasyOCR:</strong> Deep learning-based OCR for complex layouts and fallback scenarios.</li>
  <li><strong>Camelot:</strong> PDF table extraction using stream detection algorithm.</li>
  <li><strong>OpenCV & NumPy:</strong> Image preprocessing and transformations.</li>
  <li><strong>Gradio:</strong> Web-based interface for interactive usage.</li>
  <li><strong>Python Libraries:</strong> Pandas, PDF2Image, regex, json for structured data processing.</li>
</ul>

<hr>

<br>
<h2 align="center">Installation</h2>
<br>

<pre>
# Clone the repository
git clone https://github.com/YourUsername/Intelligent-Document-Understanding.git
cd Intelligent-Document-Understanding

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR if needed
sudo apt-get install tesseract-ocr    # Linux
brew install tesseract                # Mac
</pre>

<hr>

<br>
<h2 align="center">Usage</h2>
<br>

<pre>
# Run the Gradio UI
python app.root.py

# Upload a PDF or image and enter comma-separated keywords.
# The system will provide structured JSON output with:
# - Headings
# - Paragraphs
# - Key-Value pairs
# - Contacts
# - Tables
# - Abstract/Summary
</pre>

<hr>

<br>
<h2 align="center">Project Architecture</h2>
<br>

<p>
The system uses a modular pipeline architecture:
</p>
<ul>
  <li><strong>File Loading:</strong> Converts PDFs/images to OpenCV-compatible format.</li>
  <li><strong>Preprocessing:</strong> Minimal preprocessing for Tesseract, adaptive preprocessing for EasyOCR.</li>
  <li><strong>OCR Extraction:</strong> Tesseract first, then EasyOCR fallback for accuracy.</li>
  <li><strong>Text Structuring:</strong> Paragraphs, headings, key-value pairs.</li>
  <li><strong>Contact Extraction:</strong> Emails, phone numbers, URLs via regex.</li>
  <li><strong>Table Extraction:</strong> Camelot for PDFs containing tables.</li>
  <li><strong>Keyword-based Abstract:</strong> Extracts relevant sentences and generates summary.</li>
  <li><strong>Output:</strong> JSON with structured document data.</li>
</ul>

<hr>

<br>
<br>
<h2 align="center">Contact & Contribution</h2>
<br>

<p>
Have feedback, want to collaborate, or extend this project?<br>
Let’s connect and enhance intelligent document understanding systems together.
</p>

<p align="center">
<img src="https://img.shields.io/badge/Email-maylzahid588@gmail.com-blue?style=for-the-badge" alt="Email">
<img src="https://img.shields.io/badge/LinkedIn-HamaylZahid-blue?style=for-the-badge" alt="LinkedIn"> 
<a href="https://www.linkedin.com/in/hamaylzahid/"></a> 
<img src="https://img.shields.io/badge/GitHub-hamaylzahid-black?style=for-the-badge" alt="GitHub"> 
<a href="https://github.com/hamaylzahid"></a>
</p>

<p>
Found this project helpful? Give it a ⭐ star.<br>
Want to contribute or improve it? Submit a pull request and join the development. 
</p>

<br>
<h2 align="center">License</h2>
<br>

<p align="center">
This project is licensed under the <strong>MIT License</strong> and is open for use, modification, and distribution.<br>
Developed with computer vision principles and intelligent document processing in mind.
</p>


<p align="center">
Designed for intelligent document analysis, structured extraction, and analytics showcase.
</p>
