# Quick Start Guide

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```

## Features Overview

### 🛡️ Scam Awareness
Navigate to the "Awareness" section to learn about 9 different types of online scams including:
- Phishing
- Cryptocurrency scams
- Investment fraud
- Tech support scams
- And more...

### 🧠 Knowledge Quiz
Test your scam detection skills with 12 interactive questions. Get instant feedback and learn from detailed explanations.

### 🔍 Scam Checker
Analyze suspicious content:
1. Click "Scam Checker" in the navigation
2. Choose the type (Email, URL, or Message)
3. Paste the content
4. Get instant risk analysis

### 🤖 AI Content Detector
Verify authenticity of digital media:
1. Click "AI Detector" in the navigation
2. Choose media type (Image, Audio, or Video)
3. Upload or drag-and-drop your file
4. Get AI probability analysis

### 📚 Resources
Access official reporting channels and educational resources.

### 🚩 Report Scams
Help protect others by reporting scams you've encountered.

## Tips for Best Experience

1. **Start with Awareness**: Learn about different scam types first
2. **Take the Quiz**: Test your knowledge
3. **Use the Tools**: Try the Scam Checker and AI Detector with sample content
4. **Stay Updated**: Bookmark the Resources page for quick access to reporting agencies

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change port number
```

### Module Not Found Error
Ensure all dependencies are installed:
```bash
pip install --upgrade -r requirements.txt
```

## Security Note

This is an educational tool. For actual security concerns:
- Contact your bank immediately if you've shared financial information
- Report scams to FTC: https://reportfraud.ftc.gov
- File a complaint with IC3: https://www.ic3.gov

## Support

For issues or questions, refer to the README.md file for detailed documentation.

---

**Stay Safe Online! 🛡️**
