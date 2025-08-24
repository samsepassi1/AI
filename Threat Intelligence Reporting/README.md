# Threat Intelligence Reporting System

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

An automated threat intelligence reporting system that fetches, analyzes, and delivers comprehensive threat intelligence reports via email using the AlienVault OTX (Open Threat Exchange) API.


## 🔍 Overview

This Python-based threat intelligence reporting system automates the process of collecting, analyzing, and distributing threat intelligence data from AlienVault's OTX API. The system generates comprehensive PDF reports with visualizations and delivers them via email, making it ideal for cybersecurity teams, SOC analysts, and security researchers.

### Key Benefits

- **Automated Intelligence Gathering**: Continuously monitors threat intelligence feeds
- **Visual Analytics**: Generates charts and graphs for better threat landscape understanding
- **Professional Reporting**: Creates PDF reports with detailed threat pulse information
- **Flexible Scheduling**: Supports both real-time and scheduled reporting
- **Email Integration**: Automatic delivery to stakeholders and team members

## ✨ Features

### 🔄 Data Collection & Processing
- **OTX API Integration**: Fetches subscribed threat pulses from AlienVault OTX
- **Data Transformation**: Converts JSON responses to structured Pandas DataFrames
- **Intelligent Filtering**: Extracts relevant threat intelligence attributes
- **Error Handling**: Robust error handling for API connectivity issues

### 📊 Data Visualization
- **Author Analysis**: Bar charts showing threat pulse distribution by authors
- **Tag Analytics**: Pie charts highlighting the most common threat tags
- **Trend Analysis**: Visual representation of threat intelligence patterns
- **Customizable Charts**: Configurable chart styles and formats

### 📄 Report Generation
- **Professional PDF Reports**: Multi-page reports with structured layouts
- **Detailed Pulse Information**: Individual pages for each threat pulse
- **Visual Integration**: Embedded charts and graphs
- **Metadata Inclusion**: Timestamps, IDs, descriptions, and tags

### 📧 Email Automation
- **SMTP Integration**: Secure email delivery via SMTP protocols
- **Attachment Support**: PDF reports as email attachments
- **Customizable Templates**: Configurable email subjects and bodies
- **Multiple Recipients**: Support for distribution lists

### ⏰ Scheduling Options
- **Real-time Reporting**: Immediate report generation (`ThreatIntelNow.py`)
- **Daily Automation**: Scheduled daily reports (`ThreatIntelDaily.py`)
- **Flexible Timing**: Customizable schedule configurations
- **Background Processing**: Continuous operation support

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OTX API       │───▶│  Data Processing │───▶│  Visualization  │
│   (AlienVault)  │    │  (Pandas)        │    │  (Matplotlib)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Email Delivery│◀───│  PDF Generation  │◀───│  Report Builder │
│   (SMTP)        │    │  (FPDF)          │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- **Python**: Version 3.7 or higher
- **OTX API Key**: Free account at [AlienVault OTX](https://otx.alienvault.com/)
- **Email Account**: SMTP-enabled email account (Gmail, Outlook, etc.)
- **Operating System**: Windows, macOS, or Linux

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Threat Intelligence Reporting"
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv threat-intel-env

# Activate virtual environment
# On Windows:
threat-intel-env\Scripts\activate
# On macOS/Linux:
source threat-intel-env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies Overview

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | Latest | HTTP requests to OTX API |
| `pandas` | Latest | Data manipulation and analysis |
| `matplotlib` | Latest | Data visualization and charting |
| `fpdf` | Latest | PDF report generation |
| `apscheduler` | Latest | Task scheduling (Daily script) |

## ⚙️ Configuration

### Environment Variables Setup

Create a `.env` file in the project root directory or set the following environment variables:

```bash
# OTX API Configuration
OTX_API_KEY=your_otx_api_key_here

# Email Configuration
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
RECEIVER_EMAIL=recipient@company.com

# Optional: Custom file names
REPORT_PDF=threat_intelligence_report.pdf
BAR_CHART=author_distribution.png
PIE_CHART=tag_distribution.png
```

### Getting Your OTX API Key

1. Visit [AlienVault OTX](https://otx.alienvault.com/)
2. Create a free account or log in
3. Navigate to your profile settings
4. Generate an API key
5. Copy the key to your environment variables

### Email Configuration

#### For Gmail Users:
1. Enable 2-Factor Authentication
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password in `EMAIL_PASSWORD`

#### For Other Email Providers:
- Ensure SMTP is enabled
- Use appropriate SMTP settings
- May require app-specific passwords

## 🎯 Usage

### Real-time Report Generation

Generate and send a report immediately:

```bash
python ThreatIntelNow.py
```

### Scheduled Daily Reports

Start the daily automated reporting service:

```bash
python ThreatIntelDaily.py
```

The daily script will:
- Run continuously in the background
- Generate reports daily at 4:00 PM
- Send reports via email automatically
- Log all activities and errors

### Customizing Schedule

To modify the daily schedule, edit the scheduler configuration in `ThreatIntelDaily.py`:

```python
# Change the time (24-hour format)
scheduler.add_job(main, 'cron', hour=16, minute=0)  # 4:00 PM
```

## 📁 Scripts Description

### `ThreatIntelNow.py`
- **Purpose**: Immediate report generation
- **Use Case**: On-demand threat intelligence reports
- **Execution**: Single run, then exits
- **Best For**: Manual reporting, testing, ad-hoc analysis

### `ThreatIntelDaily.py`
- **Purpose**: Automated daily reporting
- **Use Case**: Continuous threat intelligence monitoring
- **Execution**: Runs continuously with scheduled tasks
- **Best For**: Production environments, regular monitoring

### Key Functions

| Function | Purpose |
|----------|---------|
| `fetch_data()` | Retrieves data from OTX API |
| `generate_table()` | Converts JSON to DataFrame |
| `generate_bar_chart()` | Creates author distribution chart |
| `generate_pie_chart()` | Creates tag distribution chart |
| `generate_pdf_report()` | Compiles PDF report |
| `send_email_with_attachment()` | Sends report via email |
| `add_pulse_to_pdf()` | Adds individual pulse details |

## 📊 Output Examples

### Generated Files

```
project_directory/
├── threat_intelligence_report.pdf    # Main PDF report
├── author_distribution.png           # Bar chart
├── tag_distribution.png             # Pie chart
└── threat_intel.log                 # Application logs
```

### Report Contents

1. **Title Page**: Report metadata and generation timestamp
2. **Author Distribution**: Bar chart showing pulse authors
3. **Tag Analysis**: Pie chart of common threat tags
4. **Detailed Pulses**: Individual pages for each threat pulse with:
   - Pulse ID and name
   - Author information
   - Associated tags
   - Creation timestamp
   - Detailed description

### Email Format

```
Subject: Daily Threat Intelligence Report - [Date]

Body:
Please find attached the daily threat intelligence report 
generated from AlienVault OTX data.

Report includes:
- Threat pulse analysis
- Author distribution charts
- Tag frequency analysis
- Detailed pulse information

Generated on: [Timestamp]
```

## 🔧 Troubleshooting

### Common Issues

#### API Connection Errors
```
Error: Failed to fetch data from OTX API
```
**Solutions:**
- Verify your OTX API key is correct
- Check internet connectivity
- Ensure OTX service is operational

#### Email Sending Failures
```
Error: Failed to send email
```
**Solutions:**
- Verify email credentials
- Check SMTP settings
- Ensure "Less secure app access" is enabled (Gmail)
- Use app-specific passwords for 2FA accounts

#### Missing Dependencies
```
ModuleNotFoundError: No module named 'requests'
```
**Solution:**
```bash
pip install -r requirements.txt
```

#### Permission Errors
```
PermissionError: [Errno 13] Permission denied
```
**Solutions:**
- Run with appropriate permissions
- Check file/directory write permissions
- Ensure output directory exists

### Logging

The application generates detailed logs in `threat_intel.log`:

```bash
# View recent logs
tail -f threat_intel.log

# Search for errors
grep "ERROR" threat_intel.log
```

### Debug Mode

Enable debug logging by modifying the logging level:

```python
logger.setLevel(logging.DEBUG)
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit Changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to Branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to functions
- Include unit tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AlienVault OTX**: For providing the threat intelligence API
- **Python Community**: For the excellent libraries used in this project
- **Contributors**: Thank you to all contributors who help improve this project

## 📞 Support

For support, questions, or feature requests:

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: [Wiki](https://github.com/your-repo/wiki)
- **Email**: support@yourproject.com

---

**⚠️ Security Note**: Never commit API keys, passwords, or sensitive credentials to version control. Always use environment variables or secure configuration files.

**📈 Version**: 1.0.0 | **Last Updated**: 2024
