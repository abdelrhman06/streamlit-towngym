# 🏋️ Towngym Corporate Leads Management System

A professional Streamlit application for collecting and managing corporate gym partnership leads with real-time Google Sheets integration.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)

## 🌟 Features

### Lead Collection Form
- ✅ Simple, clean form with validation
- ✅ 9 essential fields for lead capture
- ✅ Automatic timestamp tracking
- ✅ Real-time Google Sheets sync
- ✅ Success confirmation with animations

### Admin Dashboard
- 📊 **Key Metrics:** Total leads, interest level breakdown with percentages
- 🔍 **Search:** Find leads by company name, contact, or industry
- 🆕 **Recent Leads:** View leads from the last 7 days
- 📈 **Charts:** Location, Industry, and Interest Level distributions
- 🏆 **Top Leads:** Score-based ranking system
- 🔎 **Advanced Filters:** Filter by Location, Interest, and Industry
- 📋 **Expandable Cards:** Quick view of lead details with LinkedIn links
- 📥 **CSV Export:** Download filtered data
- 🔄 **Refresh:** Real-time data updates

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Project with Sheets API enabled
- Google Service Account credentials

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/abdelrhman06/streamlit-towngym.git
cd streamlit-towngym
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up Google Sheets**

#### Create Google Sheet
- Create a new Google Sheet named anything you want
- Note the Sheet ID from the URL
- Update `SPREADSHEET_ID` in `main.py`

#### Create Service Account
- Go to [Google Cloud Console](https://console.cloud.google.com)
- Create a new project
- Enable **Google Sheets API**
- Create Service Account credentials
- Download the JSON key file as `creds.json`
- Place `creds.json` in the project root

#### Share the Sheet
- Open your Google Sheet
- Click **Share**
- Add the service account email (from `creds.json`)
- Give **Editor** access

4. **Run the app**
```bash
streamlit run main.py
```

## 🔧 Configuration

### Admin Password
Default password: `towngym2025`

To change it, create `.streamlit/secrets.toml`:
```toml
ADMIN_PASSWORD = "your_secure_password"
```

### Spreadsheet ID
Update in `main.py`:
```python
SPREADSHEET_ID = 'your-spreadsheet-id-here'
```

## 📊 Data Structure

The app creates a Google Sheet with these columns:
- Timestamp
- Company Name
- Industry
- Size
- Location
- HR/Contact Name
- Role
- LinkedIn Link
- Interest Level
- Notes

## 🌐 Deployment on Streamlit Cloud

1. **Push to GitHub** (if not already done)
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Click "New app"
- Select your repository
- Set main file: `main.py`
- Click "Deploy"

3. **Add Secrets**
In Streamlit Cloud settings, add your secrets:
```toml
ADMIN_PASSWORD = "your_password"

[creds]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
universe_domain = "googleapis.com"
```

## 📁 Project Structure

```
streamlit-towngym/
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── creds.json          # Service account credentials (DO NOT COMMIT)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## 🔒 Security Notes

**IMPORTANT:**
- Never commit `creds.json` to Git
- Always use `.gitignore` to exclude credentials
- Use Streamlit secrets for production deployment
- Change default admin password

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Towngym Team**
- Location: New Maadi, Cairo
- Corporate Partnership Program

## 🐛 Troubleshooting

### Error: Google Sheets API not enabled
- Enable Google Sheets API in Google Cloud Console
- Wait 1-2 minutes for propagation

### Error: Permission denied
- Share the Google Sheet with your service account email
- Grant Editor access

### Error: creds.json not found
- Ensure `creds.json` is in the project root
- Check file name is exactly `creds.json`

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Open an issue on GitHub
3. Contact the development team

---

Made with ❤️ by Towngym Team | Powered by Streamlit & Google Sheets
