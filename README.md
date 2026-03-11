ANVCONSULTA

Automated monitoring system for ANVISA publications in the Diário Oficial da União (DOU).

ANVCONSULTA continuously monitors official publications, analyzes document content, and automatically sends alerts when configured expressions (company names, products, etc.) appear in new regulatory acts.

The system was designed to replace manual daily monitoring of the DOU for companies operating in regulated sectors.

Overview

ANVCONSULTA works as a continuous monitoring pipeline:

DOU Publication
       ↓
PDF Download
       ↓
Text Extraction
       ↓
Keyword Analysis
       ↓
Alert Generation
       ↓
Email Notification

Each client can configure their own expressions (keywords) and email recipients.

When a new publication contains one of the configured expressions, the system automatically sends an alert with:

the detected expression

a short AI-generated summary

the original publication link

a PDF with highlighted matches

Key Features
Automated monitoring

Continuously checks for new ANVISA-related publications.

Expression-based filtering

Clients can monitor:

company names

product names

regulatory terms

Intelligent matching

The analyzer prevents false positives by applying different rules:

long expressions → substring match

short single words → whole word match

Example:

Keyword	Text	Result
osang	rosangela	ignored
osang	osang ltda	match
Email alerts

When a match is found, the system sends a notification containing:

expression detected

AI summary of the act

link to the official publication

highlighted PDF

PDF highlighting

A copy of the official PDF is generated with the detected expressions highlighted.

Multi-client support

Each client has:

independent keyword configuration

multiple email recipients

activation schedules

Deduplication system

Alerts are never sent twice for the same match.

This is handled through a hash-based deduplication system stored in the database.

Architecture
ANVCONSULTA
│
├── Monitor Engine
│   Fetches and processes new acts
│
├── Analyzer
│   Detects expressions in extracted text
│
├── Alert Engine
│   Generates notifications and summaries
│
├── PDF Highlighter
│   Highlights detected expressions
│
└── Client Dashboard
    Manage emails, keywords and alerts
Tech Stack

Backend:

Python

FastAPI

Uvicorn

Document processing:

PyMuPDF (fitz)

Database:

SQLite

Frontend:

HTML

Vanilla JavaScript

Infrastructure:

Linux server

systemd service

journalctl logging

Project Structure
backend/
│
├── core/
│   ├── analyzer.py
│   ├── pdf_highlighter.py
│   ├── email_sender.py
│   ├── monitor_state.py
│   └── ia_resumo.py
│
├── database.py
├── app.py
│
client/
│
├── dashboard.html
├── dashboard.js
│
monitor.db
Matching Logic

Expressions are processed as single strings.

Two matching strategies are used:

Long expressions

Used for company names or phrases.

"una medic ltda"

Matching rule:

expression in normalized_text
Short keywords

To avoid false positives, short single words use word boundaries.

Example:

\bmed\b

This prevents matches such as:

med → medicina
Alert Workflow
New act detected
       ↓
PDF downloaded
       ↓
Text extracted
       ↓
Expressions analyzed
       ↓
AI summary generated
       ↓
PDF highlighted
       ↓
Alert stored
       ↓
Email sent
Running the system

The service runs continuously via systemd.

Service example:

anvconsulta.service

Start service:

systemctl start anvconsulta

Check logs:

journalctl -u anvconsulta -f
Database Tables

Main tables:

clientes
emails
keywords
alerts
processed_acts
clientes

Stores system clients.

emails

Email recipients for alerts.

keywords

Expressions monitored by the system.

alerts

Alert history.

processed_acts

Prevents reprocessing the same publication.

Configuration

Keywords can be configured with optional time windows:

hora_inicio
hora_fim

This allows alerts to be restricted to specific hours.

Motivation

Monitoring the Diário Oficial manually is time-consuming and error-prone.

ANVCONSULTA automates this process, ensuring that relevant publications are detected immediately without requiring manual daily searches.

Status

Currently running in production with active monitoring of ANVISA publications.

License

Private project.
