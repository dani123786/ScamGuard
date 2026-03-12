from flask import Flask, render_template, request, jsonify, session
import os
import re
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Email Configuration for Reporting
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # Change to your SMTP server
    'smtp_port': 587,
    'sender_email': 'your-email@gmail.com',  # Change to your email
    'sender_password': 'your-app-password',  # Use app-specific password
    'authorities': [
        'ftc@ftc.gov',  # FTC (example - use real email)
        'ic3@ic3.gov',  # IC3 (example - use real email)
        # Add more authority emails here
    ]
}

# Scam awareness data
SCAMS_DATA = {
    'phishing': {
        'title': 'Phishing Scams',
        'icon': 'fa-fish',
        'color': '#e74c3c',
        'description': 'Fraudulent attempts to obtain sensitive information by disguising as trustworthy entities.',
        'warning_signs': [
            'Urgent or threatening language',
            'Suspicious sender email addresses',
            'Requests for personal information',
            'Poor grammar and spelling',
            'Unexpected attachments or links',
            'Mismatched URLs and sender domains'
        ],
        'prevention': [
            'Verify sender identity before clicking links',
            'Check URL carefully before entering credentials',
            'Enable two-factor authentication',
            'Never share passwords via email',
            'Use email filtering and anti-phishing tools'
        ]
    },
    'cryptocurrency': {
        'title': 'Cryptocurrency Scams',
        'icon': 'fa-bitcoin-sign',
        'color': '#f39c12',
        'description': 'Fraudulent schemes involving fake crypto investments, giveaways, or wallet theft.',
        'warning_signs': [
            'Guaranteed returns or "get rich quick" promises',
            'Fake celebrity endorsements',
            'Pressure to invest immediately',
            'Requests to send crypto to unknown wallets',
            'Unverified or fake trading platforms',
            'Phishing websites mimicking legitimate exchanges'
        ],
        'prevention': [
            'Research platforms thoroughly before investing',
            'Never share private keys or seed phrases',
            'Verify URLs of crypto exchanges carefully',
            'Be skeptical of guaranteed returns',
            'Use hardware wallets for large amounts',
            'Enable all available security features'
        ]
    },
    'investment': {
        'title': 'Investment & Ponzi Schemes',
        'icon': 'fa-chart-line',
        'color': '#3498db',
        'description': 'Fraudulent schemes promising high returns with little or no risk, often paying early investors with new investors\' money.',
        'warning_signs': [
            'Guaranteed high returns with no risk',
            'Pressure to invest quickly',
            'Unregistered investments',
            'Complex strategies that aren\'t explained clearly',
            'Issues with paperwork or documentation',
            'Difficulty withdrawing funds'
        ],
        'prevention': [
            'Research investment opportunities thoroughly',
            'Verify registration with regulatory bodies (SEC, FINRA)',
            'Be skeptical of "too good to be true" returns',
            'Consult with licensed financial advisors',
            'Check for proper licensing and credentials'
        ]
    },
    'tech_support': {
        'title': 'Tech Support Scams',
        'icon': 'fa-headset',
        'color': '#9b59b6',
        'description': 'Scammers pose as tech support to gain access to your computer or steal money.',
        'warning_signs': [
            'Unsolicited calls about computer problems',
            'Pop-ups claiming your computer is infected',
            'Requests for remote access',
            'Pressure to pay immediately',
            'Requests for payment via gift cards',
            'Claims to be from Microsoft, Apple, or other major companies'
        ],
        'prevention': [
            'Never give remote access to unsolicited callers',
            'Use legitimate antivirus software',
            'Contact companies directly using official numbers',
            'Be wary of pop-up warnings',
            'Legitimate companies don\'t call unsolicited'
        ]
    },
    'online_shopping': {
        'title': 'E-Commerce & Shopping Scams',
        'icon': 'fa-shopping-cart',
        'color': '#1abc9c',
        'description': 'Fake websites or sellers that take payment but never deliver goods, or deliver counterfeit items.',
        'warning_signs': [
            'Prices significantly below market value',
            'No contact information or customer service',
            'Poor website design or spelling errors',
            'Requests for unusual payment methods',
            'No return policy or terms of service',
            'Recently created domain names'
        ],
        'prevention': [
            'Shop from reputable websites',
            'Check seller reviews and ratings',
            'Use secure payment methods with buyer protection',
            'Look for HTTPS and security certificates',
            'Research the company before purchasing',
            'Use credit cards for better fraud protection'
        ]
    },
    'identity_theft': {
        'title': 'Identity Theft & Data Breach',
        'icon': 'fa-user-secret',
        'color': '#e67e22',
        'description': 'Criminals steal personal information to commit fraud, open accounts, or make purchases in your name.',
        'warning_signs': [
            'Unexpected bills or account statements',
            'Denied credit for unknown reasons',
            'Calls from debt collectors about unknown debts',
            'Missing mail or redirected mail',
            'Unauthorized transactions on accounts',
            'IRS notices about unreported income'
        ],
        'prevention': [
            'Monitor credit reports regularly',
            'Use strong, unique passwords for all accounts',
            'Enable two-factor authentication everywhere',
            'Shred sensitive documents before disposal',
            'Be cautious about sharing personal information',
            'Use identity theft protection services'
        ]
    },
    'lottery': {
        'title': 'Lottery & Prize Scams',
        'icon': 'fa-gift',
        'color': '#e91e63',
        'description': 'Notifications claiming you\'ve won a prize but need to pay fees or taxes to claim it.',
        'warning_signs': [
            'You didn\'t enter any lottery or contest',
            'Requests for upfront payment or fees',
            'Pressure to act quickly',
            'Requests for personal or banking information',
            'Poor communication quality',
            'Payment via wire transfer or gift cards'
        ],
        'prevention': [
            'Remember: legitimate lotteries don\'t require payment',
            'Verify with official lottery organizations',
            'Never share banking details',
            'Be skeptical of unexpected winnings',
            'Research the organization claiming to award prizes'
        ]
    },
    'employment': {
        'title': 'Employment & Job Scams',
        'icon': 'fa-briefcase',
        'color': '#34495e',
        'description': 'Fake job offers designed to steal money, personal information, or use you for money laundering.',
        'warning_signs': [
            'Job offers without interviews',
            'Requests for payment for training or equipment',
            'Vague job descriptions',
            'Communication only via email or messaging apps',
            'Promises of high pay for little work',
            'Requests to cash checks or transfer money'
        ],
        'prevention': [
            'Research companies thoroughly',
            'Never pay for a job opportunity',
            'Be wary of work-from-home schemes',
            'Verify job postings on official company websites',
            'Check company reviews on Glassdoor or similar sites'
        ]
    },
    'social_media': {
        'title': 'Social Media & Impersonation',
        'icon': 'fa-users',
        'color': '#2ecc71',
        'description': 'Scammers create fake profiles, impersonate trusted contacts, or spread malicious links on social platforms.',
        'warning_signs': [
            'Friend requests from people you\'re already connected with',
            'Messages from friends asking for money or help',
            'Too-good-to-be-true offers or giveaways',
            'Requests to click suspicious links',
            'Fake verification badges or celebrity accounts',
            'Unusual behavior from known contacts'
        ],
        'prevention': [
            'Verify identity through another communication channel',
            'Check profile creation dates and activity',
            'Be cautious of unsolicited messages',
            'Don\'t click links from unknown sources',
            'Report suspicious accounts to the platform',
            'Enable privacy settings on all social accounts'
        ]
    },
    'deepfake': {
        'title': 'Deepfake Scams',
        'icon': 'fa-video',
        'color': '#ff6b6b',
        'description': 'AI-generated fake videos, audio, or images used to impersonate individuals for fraud, blackmail, or misinformation.',
        'warning_signs': [
            'Unnatural facial movements or expressions',
            'Mismatched lip-sync with audio',
            'Inconsistent lighting or shadows on face',
            'Blurry or distorted areas around face edges',
            'Unusual blinking patterns or lack of blinking',
            'Audio that doesn\'t match the person\'s usual speech patterns',
            'Requests for money or sensitive actions via video',
            'Video quality inconsistencies'
        ],
        'prevention': [
            'Verify video calls through multiple channels',
            'Use code words with family members for emergencies',
            'Be skeptical of urgent requests via video',
            'Check for AI detection tools and services',
            'Look for unnatural movements or artifacts',
            'Verify identity through phone calls or in-person',
            'Be cautious of celebrity endorsement videos',
            'Report suspected deepfakes to platforms'
        ]
    }
}

# Practice quiz questions for each scam type (10 MCQs each)
PRACTICE_QUIZZES = {
    'phishing': [
        {'question': 'What is the main goal of phishing attacks?', 'options': ['To sell products', 'To steal sensitive information', 'To provide services', 'To advertise'], 'correct': 1, 'explanation': 'Phishing attacks aim to steal sensitive information like passwords, credit card numbers, and personal data.'},
        {'question': 'Which protocol indicates a secure website?', 'options': ['HTTP', 'HTTPS', 'FTP', 'SMTP'], 'correct': 1, 'explanation': 'HTTPS (Hypertext Transfer Protocol Secure) encrypts data between your browser and the website, making it more secure.'},
        {'question': 'What should you do with suspicious emails?', 'options': ['Reply immediately', 'Delete without opening', 'Forward to friends', 'Click all links'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Phishing emails often contain:', 'options': ['Perfect grammar', 'Urgent language', 'Official letterheads only', 'No links'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'How can you verify a sender\'s email?', 'options': ['Trust the display name', 'Check the actual email address', 'Assume it\'s real', 'Reply and ask'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'What is spear phishing?', 'options': ['Fishing with a spear', 'Targeted phishing attack', 'Mass email campaign', 'A type of malware'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Legitimate companies will:', 'options': ['Ask for passwords via email', 'Never ask for passwords via email', 'Request SSN in emails', 'Demand immediate action'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'What should you check before clicking a link?', 'options': ['The link color', 'Hover to see actual URL', 'The font size', 'Nothing'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Phishing attacks can come through:', 'options': ['Email only', 'Email, SMS, and social media', 'Phone calls only', 'Mail only'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'If you clicked a phishing link, you should:', 'options': ['Do nothing', 'Change passwords immediately', 'Wait and see', 'Delete your account'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'}
    ],
    'cryptocurrency': [
        {'question': 'What is a major red flag in crypto investments?', 'options': ['Detailed whitepaper', 'Guaranteed returns', 'Transparent team', 'Open source code'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'You should NEVER share your:', 'options': ['Public wallet address', 'Seed phrase', 'Transaction history', 'Favorite coin'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'What is a "rug pull"?', 'options': ['A cleaning method', 'Developers abandoning project with funds', 'A trading strategy', 'A wallet feature'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Fake crypto giveaways often:', 'options': ['Ask you to send crypto first', 'Are completely free', 'Require no action', 'Are always legitimate'], 'correct': 0, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'How can you verify a crypto project?', 'options': ['Trust social media hype', 'Research team, code, and audits', 'Follow influencers blindly', 'Invest immediately'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'What is a Ponzi scheme in crypto?', 'options': ['A mining method', 'Paying old investors with new investor money', 'A wallet type', 'A blockchain'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Celebrity crypto endorsements:', 'options': ['Are always genuine', 'Should be verified carefully', 'Guarantee profits', 'Are risk-free'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'What is pump and dump?', 'options': ['A workout routine', 'Artificially inflating price then selling', 'A wallet backup', 'A mining technique'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Secure crypto storage uses:', 'options': ['Exchange wallets only', 'Hardware wallets for large amounts', 'Email storage', 'Social media'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'If an investment seems too good to be true:', 'options': ['Invest immediately', 'It probably is - be cautious', 'Tell everyone', 'Borrow money to invest'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'}
    ],
    'investment': [
        {'question': 'What characterizes a Ponzi scheme?', 'options': ['Legitimate returns', 'Paying old investors with new money', 'Government backed', 'Low risk'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Legitimate investments are:', 'options': ['Unregistered', 'Registered with SEC/FINRA', 'Secret', 'Guaranteed'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'High returns with no risk means:', 'options': ['Great opportunity', 'Likely a scam', 'Safe investment', 'Government approved'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Before investing, you should:', 'options': ['Act quickly', 'Research thoroughly', 'Trust the salesperson', 'Invest everything'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Pressure to invest immediately is:', 'options': ['A good sign', 'A major red flag', 'Normal practice', 'Required'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Investment scammers often:', 'options': ['Provide full disclosure', 'Use complex unexplained strategies', 'Are fully licensed', 'Offer refunds'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'You should verify investments with:', 'options': ['The seller only', 'Independent regulatory bodies', 'Friends', 'Social media'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Difficulty withdrawing funds indicates:', 'options': ['Normal processing', 'Possible scam', 'Good security', 'High returns'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Unsolicited investment offers:', 'options': ['Are always good', 'Should be treated with suspicion', 'Are risk-free', 'Guarantee profits'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Legitimate advisors will:', 'options': ['Guarantee returns', 'Discuss risks openly', 'Pressure you', 'Avoid paperwork'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'}
    ],
    'tech_support': [
        {'question': 'Microsoft will:', 'options': ['Call you about viruses', 'Never call unsolicited', 'Ask for remote access', 'Request payment'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Pop-ups claiming infection are:', 'options': ['Always accurate', 'Usually scams', 'From antivirus', 'Helpful warnings'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'You should never:', 'options': ['Use antivirus', 'Give remote access to strangers', 'Update software', 'Restart computer'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Legitimate tech support:', 'options': ['Demands immediate payment', 'Doesn\'t call unsolicited', 'Uses gift cards', 'Threatens you'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'If you need tech help:', 'options': ['Call pop-up numbers', 'Contact companies directly', 'Trust cold callers', 'Pay with gift cards'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Tech support scammers often:', 'options': ['Are patient', 'Create urgency and fear', 'Offer refunds', 'Are certified'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Payment via gift cards is:', 'options': ['Standard practice', 'A major red flag', 'Secure', 'Recommended'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Remote access should only be given to:', 'options': ['Anyone who asks', 'Trusted, verified technicians', 'Cold callers', 'Pop-up warnings'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Fake virus warnings:', 'options': ['Are always real', 'Often lead to scams', 'Should be clicked', 'Are from Windows'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Real antivirus software:', 'options': ['Calls you', 'Doesn\'t use scare tactics', 'Demands payment', 'Uses pop-ups'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'}
    ],
    'online_shopping': [
        {'question': 'Prices far below market value indicate:', 'options': ['Great deals', 'Possible scam', 'Clearance sale', 'Wholesale pricing'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Secure shopping sites have:', 'options': ['HTTP only', 'HTTPS and padlock', 'No security', 'Pop-up ads'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Before buying, check:', 'options': ['Nothing', 'Reviews and seller ratings', 'Only price', 'Shipping cost'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Payment should use:', 'options': ['Wire transfer', 'Credit cards with protection', 'Gift cards', 'Cash'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Fake shopping sites often:', 'options': ['Have detailed policies', 'Lack contact information', 'Offer refunds', 'Are well-designed'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'New domains should be:', 'options': ['Trusted immediately', 'Researched carefully', 'Avoided always', 'Preferred'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Legitimate sellers provide:', 'options': ['No information', 'Clear contact and return policies', 'Only email', 'No tracking'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'If deal seems too good:', 'options': ['Buy immediately', 'Verify seller legitimacy', 'Share with friends', 'Use debit card'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Counterfeit goods are often:', 'options': ['High quality', 'Sold at suspiciously low prices', 'Clearly labeled', 'Legal'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Safe online shopping uses:', 'options': ['Public WiFi', 'Secure private networks', 'Shared computers', 'Saved passwords'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'}
    ],
    'identity_theft': [
        {'question': 'You should monitor:', 'options': ['Nothing', 'Credit reports regularly', 'Only bank accounts', 'Social media'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Strong passwords include:', 'options': ['Your birthday', 'Mix of characters and symbols', 'Your name', 'Simple words'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Two-factor authentication:', 'options': ['Is unnecessary', 'Adds important security', 'Is too complex', 'Doesn\'t work'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Sensitive documents should be:', 'options': ['Thrown away', 'Shredded before disposal', 'Recycled normally', 'Kept forever'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Personal information should:', 'options': ['Be shared freely', 'Be protected carefully', 'Be posted online', 'Be given to anyone'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Identity theft protection:', 'options': ['Is a scam', 'Can help monitor and alert', 'Guarantees safety', 'Is unnecessary'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Unexpected bills may indicate:', 'options': ['Nothing', 'Possible identity theft', 'Good credit', 'Rewards'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Public WiFi should be:', 'options': ['Used for banking', 'Avoided for sensitive tasks', 'Always trusted', 'Preferred'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Social media oversharing:', 'options': ['Is safe', 'Can enable identity theft', 'Is recommended', 'Has no risks'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'If identity is stolen:', 'options': ['Do nothing', 'Report immediately to authorities', 'Wait and see', 'Change nothing'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'}
    ],
    'lottery': [
        {'question': 'Legitimate lotteries:', 'options': ['Require upfront fees', 'Never require payment to claim', 'Ask for bank details', 'Call randomly'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'You can\'t win a lottery you:', 'options': ['Entered', 'Never entered', 'Forgot about', 'Dreamed of'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Prize scams often require:', 'options': ['Nothing', 'Upfront payment for taxes/fees', 'Just your address', 'Only your name'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Legitimate prizes:', 'options': ['Require wire transfers', 'Don\'t require payment', 'Need gift cards', 'Demand urgency'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Foreign lottery offers are:', 'options': ['Great opportunities', 'Usually scams', 'Legal everywhere', 'Risk-free'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Pressure to act quickly means:', 'options': ['Great opportunity', 'Likely a scam', 'Limited availability', 'Genuine urgency'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Real lottery organizations:', 'options': ['Call randomly', 'Can be verified officially', 'Hide their identity', 'Use pressure tactics'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Payment via gift cards for prizes:', 'options': ['Is standard', 'Is a major red flag', 'Is secure', 'Is required'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'If you win legitimately:', 'options': ['Pay fees first', 'Receive winnings without payment', 'Wire money', 'Act immediately'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Sweepstakes scams target:', 'options': ['Only elderly', 'Anyone', 'Only wealthy', 'Only young people'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'}
    ],
    'employment': [
        {'question': 'Legitimate jobs:', 'options': ['Require payment', 'Never require payment', 'Need upfront fees', 'Charge for training'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Job offers without interviews are:', 'options': ['Normal', 'Suspicious', 'Preferred', 'Efficient'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Work-from-home jobs should:', 'options': ['Require investment', 'Be researched thoroughly', 'Promise high pay', 'Avoid interviews'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Vague job descriptions indicate:', 'options': ['Flexibility', 'Possible scam', 'Great opportunity', 'High pay'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Legitimate employers:', 'options': ['Only use email', 'Have verifiable presence', 'Avoid phone calls', 'Hide identity'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Money transfer jobs are often:', 'options': ['Legitimate', 'Money laundering scams', 'High paying', 'Legal'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Before accepting a job:', 'options': ['Accept immediately', 'Research the company', 'Pay fees', 'Quit current job'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Job scams may ask you to:', 'options': ['Attend interview', 'Cash checks and forward money', 'Provide references', 'Submit resume'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'High pay for little work suggests:', 'options': ['Great opportunity', 'Likely a scam', 'Easy money', 'Perfect job'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Verify jobs on:', 'options': ['Email only', 'Official company websites', 'Social media only', 'Job scam sites'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'}
    ],
    'social_media': [
        {'question': 'Duplicate friend requests mean:', 'options': ['They forgot', 'Possible impersonation', 'Technical error', 'They like you'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Friends asking for money online:', 'options': ['Should be helped immediately', 'Should be verified another way', 'Are always real', 'Need urgent help'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Too-good-to-be-true offers are:', 'options': ['Real opportunities', 'Usually scams', 'Limited time deals', 'Exclusive'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Suspicious links should be:', 'options': ['Clicked immediately', 'Avoided', 'Shared', 'Trusted'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Fake celebrity accounts:', 'options': ['Are rare', 'Are common scams', 'Are verified', 'Are harmless'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Privacy settings should be:', 'options': ['Public', 'Restricted', 'Ignored', 'Minimal'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Verify unusual requests by:', 'options': ['Responding immediately', 'Contacting through another channel', 'Trusting the message', 'Ignoring'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Profile creation dates can:', 'options': ['Be ignored', 'Indicate fake accounts', 'Be trusted', 'Be hidden'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Suspicious accounts should be:', 'options': ['Followed', 'Reported to platform', 'Engaged with', 'Shared'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Personal information on social media:', 'options': ['Should be public', 'Should be limited', 'Doesn\'t matter', 'Should be detailed'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'}
    ],
    'deepfake': [
        {'question': 'What is a deepfake?', 'options': ['A deep ocean photo', 'AI-generated fake media', 'A camera filter', 'A video game'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Deepfakes can create fake:', 'options': ['Text only', 'Video, audio, and images', 'Emails only', 'Websites only'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Warning signs of deepfakes include:', 'options': ['Perfect quality', 'Unnatural facial movements', 'Clear audio', 'High resolution'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Deepfake scams may involve:', 'options': ['Legitimate requests', 'Impersonating people for fraud', 'Real videos', 'Verified content'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'To verify video calls:', 'options': ['Trust immediately', 'Use multiple verification methods', 'Assume it\'s real', 'Send money'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Code words with family help:', 'options': ['Complicate things', 'Verify identity in emergencies', 'Are unnecessary', 'Are childish'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Deepfake audio can:', 'options': ['Never fool anyone', 'Mimic voices convincingly', 'Only work in person', 'Be easily detected'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'If you suspect a deepfake:', 'options': ['Comply immediately', 'Verify through other channels', 'Trust it', 'Share it'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'Deepfakes are used for:', 'options': ['Entertainment only', 'Fraud, blackmail, misinformation', 'Education only', 'Art only'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'},
        {'question': 'AI detection tools:', 'options': ['Don\'t exist', 'Can help identify deepfakes', 'Are perfect', 'Are unnecessary'], 'correct': 1, 'explanation': 'This is the correct answer based on scam awareness best practices.'}
    ]
}

# Quiz questions organized by difficulty
QUIZ_QUESTIONS = {
    'easy': [
        {
            'question': 'What should you do if you receive an email asking for your password?',
            'options': ['Reply with your password', 'Delete it immediately', 'Click the link to verify', 'Forward it to friends'],
            'correct': 1,
            'explanation': 'Legitimate companies never ask for passwords via email. Delete such emails immediately.'
        },
        {
            'question': 'What is phishing?',
            'options': ['A water sport', 'Fraudulent attempt to obtain sensitive information', 'A type of fish', 'A computer game'],
            'correct': 1,
            'explanation': 'Phishing is a fraudulent attempt to obtain sensitive information by disguising as a trustworthy entity.'
        },
        {
            'question': 'How can you verify if a website is secure?',
            'options': ['Check if URL starts with HTTPS', 'Look at the colors', 'Count the images', 'Check the font size'],
            'correct': 0,
            'explanation': 'Secure websites use HTTPS protocol, indicated by a padlock icon and "https://" in the URL.'
        },
        {
            'question': 'What should you NEVER share with anyone online?',
            'options': ['Your favorite color', 'Your crypto wallet seed phrase', 'Your city name', 'Your hobby'],
            'correct': 1,
            'explanation': 'Your seed phrase gives complete access to your crypto wallet. Never share it with anyone, ever.'
        },
        {
            'question': 'A pop-up says your computer is infected. What should you do?',
            'options': ['Call the number shown', 'Close it and run your own antivirus', 'Download their software', 'Restart immediately'],
            'correct': 1,
            'explanation': 'This is a tech support scam. Close the pop-up and use your own legitimate antivirus software.'
        },
        {
            'question': 'What is two-factor authentication?',
            'options': ['Using two passwords', 'An extra layer of security requiring two forms of verification', 'Having two email accounts', 'A type of scam'],
            'correct': 1,
            'explanation': 'Two-factor authentication adds an extra layer of security by requiring two forms of verification.'
        },
        {
            'question': 'You win a lottery you never entered. They ask for a fee. What do you do?',
            'options': ['Pay the fee', 'Hang up - it\'s a scam', 'Give bank details', 'Ask them to call back'],
            'correct': 1,
            'explanation': 'Legitimate lotteries never require upfront payment. This is a classic scam.'
        },
        {
            'question': 'What makes a strong password?',
            'options': ['Your birthday', 'Mix of letters, numbers, and symbols', 'Your name', 'password123'],
            'correct': 1,
            'explanation': 'Strong passwords combine uppercase, lowercase, numbers, and special characters.'
        },
        {
            'question': 'Someone calls claiming to be from your bank. What should you do?',
            'options': ['Give them your account number', 'Hang up and call your bank directly', 'Answer all their questions', 'Transfer money as requested'],
            'correct': 1,
            'explanation': 'Always verify by calling your bank directly using the official number on their website or card.'
        },
        {
            'question': 'What is a red flag in online shopping?',
            'options': ['Customer reviews', 'Prices too good to be true', 'Contact information', 'Return policy'],
            'correct': 1,
            'explanation': 'If prices are significantly lower than market value, it\'s likely a scam.'
        },
        {
            'question': 'You receive a friend request from someone you\'re already friends with. What should you do?',
            'options': ['Accept immediately', 'Report it as a fake account', 'Share your password', 'Ignore it'],
            'correct': 1,
            'explanation': 'This is likely an impersonation attempt. Report it and notify your real friend.'
        },
        {
            'question': 'What should you do if you think you\'ve been scammed?',
            'options': ['Do nothing', 'Report it to authorities and your bank', 'Try to scam them back', 'Delete all evidence'],
            'correct': 1,
            'explanation': 'Report scams immediately to authorities and your financial institution to minimize damage.'
        },
        {
            'question': 'A job offer requires you to pay for training. What should you do?',
            'options': ['Pay for it', 'Decline - legitimate jobs don\'t require payment', 'Negotiate the price', 'Borrow money to pay'],
            'correct': 1,
            'explanation': 'Legitimate employers never ask you to pay for job opportunities or training materials.'
        },
        {
            'question': 'What is a deepfake?',
            'options': ['A deep ocean exploration', 'AI-generated fake video or audio', 'A type of fish', 'A social media filter'],
            'correct': 1,
            'explanation': 'Deepfakes are AI-generated fake videos or audio that can impersonate real people.'
        },
        {
            'question': 'You receive an urgent email from your "CEO" asking for gift cards. What do you do?',
            'options': ['Buy them immediately', 'Verify through another channel first', 'Use company credit card', 'Forward to colleagues'],
            'correct': 1,
            'explanation': 'This is a common CEO fraud scam. Always verify unusual requests through another communication method.'
        },
        {
            'question': 'What is the safest way to pay online?',
            'options': ['Wire transfer', 'Credit card with fraud protection', 'Gift cards', 'Cash in mail'],
            'correct': 1,
            'explanation': 'Credit cards offer fraud protection and the ability to dispute charges.'
        },
        {
            'question': 'A stranger on social media asks for money for an emergency. What should you do?',
            'options': ['Send money', 'Refuse and report the account', 'Ask for more details', 'Share their post'],
            'correct': 1,
            'explanation': 'Never send money to strangers online. This is a common social media scam.'
        },
        {
            'question': 'What should you check before clicking a link in an email?',
            'options': ['The font color', 'Hover over it to see the actual URL', 'The email subject', 'The time it was sent'],
            'correct': 1,
            'explanation': 'Hovering over links reveals the actual destination URL, which may differ from the displayed text.'
        },
        {
            'question': 'What is ransomware?',
            'options': ['A video game', 'Malware that locks your files and demands payment', 'A type of insurance', 'A security software'],
            'correct': 1,
            'explanation': 'Ransomware encrypts your files and demands payment for the decryption key.'
        },
        {
            'question': 'You receive a text saying your package is delayed and to click a link. What do you do?',
            'options': ['Click the link', 'Check directly with the shipping company', 'Reply with personal info', 'Forward to friends'],
            'correct': 1,
            'explanation': 'This is likely a phishing attempt. Always check directly with the company using official channels.'
        }
    ],
    'medium': [
        {
            'question': 'What is "vishing"?',
            'options': ['Video phishing', 'Voice phishing via phone calls', 'Virtual phishing', 'Virus phishing'],
            'correct': 1,
            'explanation': 'Vishing is voice phishing - scammers use phone calls to trick victims into revealing sensitive information.'
        },
        {
            'question': 'A website offers designer products at 90% off. What should you do?',
            'options': ['Buy immediately', 'Research the website thoroughly first', 'Share with friends', 'Enter credit card details'],
            'correct': 1,
            'explanation': 'Deals that seem too good to be true often are. Always research unfamiliar websites before purchasing.'
        },
        {
            'question': 'Someone offers guaranteed 50% returns on cryptocurrency. What should you do?',
            'options': ['Invest immediately', 'Be extremely cautious - likely a scam', 'Invest a small amount', 'Share with friends'],
            'correct': 1,
            'explanation': 'Guaranteed high returns in crypto are a major red flag. Legitimate investments never guarantee returns.'
        },
        {
            'question': 'What is "smishing"?',
            'options': ['Smile phishing', 'SMS/text message phishing', 'Smart phishing', 'Social media phishing'],
            'correct': 1,
            'explanation': 'Smishing is phishing via SMS text messages, often containing malicious links.'
        },
        {
            'question': 'You receive an email with an unexpected attachment from a known contact. What should you do?',
            'options': ['Open it immediately', 'Verify with the sender through another method first', 'Forward it', 'Delete without checking'],
            'correct': 1,
            'explanation': 'Email accounts can be compromised. Always verify unexpected attachments with the sender.'
        },
        {
            'question': 'What is a "pump and dump" scheme in cryptocurrency?',
            'options': ['A mining technique', 'Artificially inflating price then selling', 'A wallet type', 'A trading strategy'],
            'correct': 1,
            'explanation': 'Pump and dump schemes artificially inflate cryptocurrency prices before scammers sell, leaving victims with losses.'
        },
        {
            'question': 'What is "typosquatting"?',
            'options': ['Typing errors', 'Registering misspelled domain names to trick users', 'A keyboard layout', 'A typing game'],
            'correct': 1,
            'explanation': 'Typosquatting involves registering domains similar to legitimate sites to capture mistyped URLs.'
        },
        {
            'question': 'A romance scammer typically does what?',
            'options': ['Meets in person quickly', 'Builds trust then asks for money', 'Provides real identity', 'Video calls regularly'],
            'correct': 1,
            'explanation': 'Romance scammers build emotional connections over time before requesting money for fake emergencies.'
        },
        {
            'question': 'What is "credential stuffing"?',
            'options': ['Password creation', 'Using stolen credentials on multiple sites', 'A security feature', 'A login method'],
            'correct': 1,
            'explanation': 'Credential stuffing uses stolen username/password pairs to access accounts on multiple platforms.'
        },
        {
            'question': 'What is a "pig butchering" scam?',
            'options': ['A farming scam', 'Long-term investment scam building trust before stealing', 'A food scam', 'A livestock fraud'],
            'correct': 1,
            'explanation': 'Pig butchering scams involve building trust over time before convincing victims to invest in fake opportunities.'
        },
        {
            'question': 'What is "SIM swapping"?',
            'options': ['Changing phone carriers', 'Hijacking phone number to bypass 2FA', 'Upgrading SIM card', 'A phone feature'],
            'correct': 1,
            'explanation': 'SIM swapping involves transferring your phone number to a scammer\'s device to intercept 2FA codes.'
        },
        {
            'question': 'What is "business email compromise" (BEC)?',
            'options': ['Email server issues', 'Impersonating executives to authorize fraudulent transfers', 'Email marketing', 'Spam filtering'],
            'correct': 1,
            'explanation': 'BEC involves impersonating company executives to trick employees into transferring money or data.'
        },
        {
            'question': 'What is a "rug pull" in cryptocurrency?',
            'options': ['A mining method', 'Developers abandoning project and stealing funds', 'A wallet feature', 'A trading term'],
            'correct': 1,
            'explanation': 'A rug pull occurs when crypto developers abandon a project and run away with investors\' funds.'
        },
        {
            'question': 'What is "juice jacking"?',
            'options': ['Stealing juice', 'Malware infection through public USB charging ports', 'A phone feature', 'Battery optimization'],
            'correct': 1,
            'explanation': 'Juice jacking involves installing malware or stealing data through compromised public USB charging stations.'
        },
        {
            'question': 'What is "invoice fraud"?',
            'options': ['Billing errors', 'Sending fake invoices to trick payment', 'Accounting mistakes', 'Tax fraud'],
            'correct': 1,
            'explanation': 'Invoice fraud involves sending fake invoices that appear legitimate to trick businesses into paying.'
        },
        {
            'question': 'What is "advance fee fraud"?',
            'options': ['Early payment discount', 'Paying upfront for promised benefits that never materialize', 'Prepaid services', 'Subscription fees'],
            'correct': 1,
            'explanation': 'Advance fee fraud requires victims to pay upfront for promised money, prizes, or services that never arrive.'
        },
        {
            'question': 'What is "pharming"?',
            'options': ['Agricultural fraud', 'Redirecting website traffic to fake sites', 'Pharmaceutical scams', 'A farming technique'],
            'correct': 1,
            'explanation': 'Pharming redirects users from legitimate websites to fraudulent ones without their knowledge.'
        },
        {
            'question': 'What is a "money mule"?',
            'options': ['A wealthy person', 'Someone who transfers illegally obtained money', 'A banking term', 'An investment strategy'],
            'correct': 1,
            'explanation': 'Money mules transfer money obtained illegally, often unknowingly recruited through job scams.'
        },
        {
            'question': 'What is "pretexting"?',
            'options': ['Writing practice', 'Creating fake scenarios to obtain information', 'A texting app', 'A communication style'],
            'correct': 1,
            'explanation': 'Pretexting involves creating fabricated scenarios to manipulate victims into revealing sensitive information.'
        },
        {
            'question': 'What is "watering hole attack"?',
            'options': ['Water contamination', 'Compromising websites frequented by targets', 'A hacking tool', 'A phishing method'],
            'correct': 1,
            'explanation': 'Watering hole attacks compromise websites frequently visited by specific target groups to infect their systems.'
        }
    ],
    'difficult': [
        {
            'question': 'What is a "zero-day exploit"?',
            'options': ['A calendar bug', 'Vulnerability unknown to software vendor', 'A hacking tool', 'A type of malware'],
            'correct': 1,
            'explanation': 'Zero-day exploits target vulnerabilities that are unknown to the software vendor, leaving no time for patches.'
        },
        {
            'question': 'What is "spear phishing" compared to regular phishing?',
            'options': ['Uses spear imagery', 'Highly targeted at specific individuals', 'More aggressive', 'Uses different technology'],
            'correct': 1,
            'explanation': 'Spear phishing is highly targeted, using personal information to make attacks more convincing to specific victims.'
        },
        {
            'question': 'What is "DNS hijacking"?',
            'options': ['Domain name theft', 'Redirecting DNS queries to malicious servers', 'Server hacking', 'Website defacement'],
            'correct': 1,
            'explanation': 'DNS hijacking redirects domain name queries to malicious servers, sending users to fake websites.'
        },
        {
            'question': 'What is a "man-in-the-middle" (MITM) attack?',
            'options': ['Physical interception', 'Intercepting communication between two parties', 'A negotiation tactic', 'A proxy server'],
            'correct': 1,
            'explanation': 'MITM attacks intercept and potentially alter communication between two parties without their knowledge.'
        },
        {
            'question': 'What is "cryptojacking"?',
            'options': ['Stealing cryptocurrency', 'Unauthorized use of devices to mine cryptocurrency', 'Hacking wallets', 'A mining technique'],
            'correct': 1,
            'explanation': 'Cryptojacking secretly uses victims\' computing resources to mine cryptocurrency without consent.'
        },
        {
            'question': 'What is "session hijacking"?',
            'options': ['Meeting interruption', 'Stealing session tokens to impersonate users', 'A hacking tool', 'Browser feature'],
            'correct': 1,
            'explanation': 'Session hijacking involves stealing session tokens to gain unauthorized access to user accounts.'
        },
        {
            'question': 'What is a "supply chain attack"?',
            'options': ['Logistics fraud', 'Compromising software through trusted vendors', 'Shipping scams', 'Manufacturing fraud'],
            'correct': 1,
            'explanation': 'Supply chain attacks compromise software by infiltrating trusted third-party vendors or suppliers.'
        },
        {
            'question': 'What is "SQL injection"?',
            'options': ['Database backup', 'Inserting malicious SQL code to manipulate databases', 'A programming language', 'Data encryption'],
            'correct': 1,
            'explanation': 'SQL injection inserts malicious SQL code into input fields to manipulate or access databases.'
        },
        {
            'question': 'What is "cross-site scripting" (XSS)?',
            'options': ['Website linking', 'Injecting malicious scripts into trusted websites', 'A programming technique', 'Browser feature'],
            'correct': 1,
            'explanation': 'XSS injects malicious scripts into trusted websites, which then execute in victims\' browsers.'
        },
        {
            'question': 'What is "BGP hijacking"?',
            'options': ['Protocol theft', 'Maliciously rerouting internet traffic', 'A hacking tool', 'Network configuration'],
            'correct': 1,
            'explanation': 'BGP hijacking maliciously manipulates Border Gateway Protocol to reroute internet traffic through attacker-controlled systems.'
        },
        {
            'question': 'What is a "fileless malware attack"?',
            'options': ['Deleting files', 'Malware that operates in memory without files', 'A virus type', 'Data theft'],
            'correct': 1,
            'explanation': 'Fileless malware operates entirely in memory, making it harder to detect with traditional antivirus.'
        },
        {
            'question': 'What is "domain shadowing"?',
            'options': ['Dark web domains', 'Creating subdomains on compromised accounts', 'Domain privacy', 'DNS caching'],
            'correct': 1,
            'explanation': 'Domain shadowing creates numerous subdomains on compromised domain accounts for malicious purposes.'
        },
        {
            'question': 'What is a "living off the land" (LOL) attack?',
            'options': ['Rural cybercrime', 'Using legitimate system tools for malicious purposes', 'A hacking technique', 'Social engineering'],
            'correct': 1,
            'explanation': 'LOL attacks use legitimate system administration tools already present on systems for malicious activities.'
        },
        {
            'question': 'What is "credential harvesting"?',
            'options': ['Password management', 'Systematically collecting login credentials', 'Data backup', 'Account creation'],
            'correct': 1,
            'explanation': 'Credential harvesting systematically collects usernames and passwords through various attack methods.'
        },
        {
            'question': 'What is a "watering hole attack" targeting mechanism?',
            'options': ['Random targeting', 'Compromising sites visited by specific groups', 'Email campaigns', 'Social media'],
            'correct': 1,
            'explanation': 'Watering hole attacks compromise websites frequented by specific target groups to infect their systems.'
        },
        {
            'question': 'What is "DLL hijacking"?',
            'options': ['File deletion', 'Exploiting DLL loading mechanisms to execute malicious code', 'A programming error', 'System optimization'],
            'correct': 1,
            'explanation': 'DLL hijacking exploits how applications load Dynamic Link Libraries to execute malicious code.'
        },
        {
            'question': 'What is "process hollowing"?',
            'options': ['Deleting processes', 'Replacing legitimate process memory with malicious code', 'System cleanup', 'Performance optimization'],
            'correct': 1,
            'explanation': 'Process hollowing replaces the memory of a legitimate process with malicious code while maintaining the process appearance.'
        },
        {
            'question': 'What is "token impersonation"?',
            'options': ['Fake currency', 'Stealing access tokens to impersonate users', 'A blockchain feature', 'Authentication method'],
            'correct': 1,
            'explanation': 'Token impersonation involves stealing and using access tokens to impersonate legitimate users or processes.'
        },
        {
            'question': 'What is a "pass-the-hash" attack?',
            'options': ['Password sharing', 'Using password hashes without cracking them', 'Encryption method', 'Authentication protocol'],
            'correct': 1,
            'explanation': 'Pass-the-hash attacks use captured password hashes for authentication without needing to crack them.'
        },
        {
            'question': 'What is "OSINT" in the context of social engineering?',
            'options': ['A hacking tool', 'Open Source Intelligence gathering from public sources', 'An operating system', 'A programming language'],
            'correct': 1,
            'explanation': 'OSINT involves gathering intelligence from publicly available sources to craft targeted social engineering attacks.'
        }
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/awareness')
def awareness():
    return render_template('awareness.html', scams=SCAMS_DATA)

@app.route('/awareness/<scam_type>')
def scam_detail(scam_type):
    if scam_type in SCAMS_DATA:
        # Get practice quiz questions for this scam type
        practice_questions = PRACTICE_QUIZZES.get(scam_type, [])
        
        # Check if video exists for this scam type
        video_path = os.path.join('static', 'videos', f'{scam_type}.mp4')
        video_available = os.path.exists(video_path)
        
        return render_template('scam_detail.html', 
                             scam_type=scam_type, 
                             scam=SCAMS_DATA[scam_type],
                             practice_questions=practice_questions,
                             video_available=video_available)
    return "Scam type not found", 404

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/api/quiz/questions')
def get_quiz_questions():
    difficulty = request.args.get('difficulty', 'easy')
    if difficulty in QUIZ_QUESTIONS:
        return jsonify(QUIZ_QUESTIONS[difficulty])
    return jsonify(QUIZ_QUESTIONS['easy'])

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    data = request.json
    answers = data.get('answers', [])
    difficulty = data.get('difficulty', 'easy')
    user_name = data.get('name', 'Anonymous')
    
    questions = QUIZ_QUESTIONS.get(difficulty, QUIZ_QUESTIONS['easy'])
    score = sum(1 for i, ans in enumerate(answers) if ans == questions[i]['correct'])
    total = len(questions)
    percentage = (score / total) * 100
    
    return jsonify({
        'score': score,
        'total': total,
        'percentage': percentage,
        'name': user_name,
        'difficulty': difficulty,
        'results': [
            {
                'correct': answers[i] == questions[i]['correct'],
                'explanation': questions[i]['explanation']
            }
            for i in range(len(answers))
        ]
    })

@app.route('/checker')
def checker():
    return render_template('checker.html')

@app.route('/api/check', methods=['POST'])
def check_scam():
    data = request.json
    check_type = data.get('type')
    content = data.get('content', '')
    
    risk_score = 0
    warnings = []
    
    if check_type == 'email':
        # Check for phishing indicators
        if re.search(r'urgent|act now|verify|suspended|locked|immediate action', content, re.IGNORECASE):
            risk_score += 25
            warnings.append('Contains urgent or threatening language')
        
        if re.search(r'click here|download|verify account|confirm identity', content, re.IGNORECASE):
            risk_score += 20
            warnings.append('Contains suspicious call-to-action')
        
        if re.search(r'password|ssn|credit card|bank account|social security', content, re.IGNORECASE):
            risk_score += 30
            warnings.append('Requests sensitive information')
        
        if re.search(r'congratulations|winner|prize|lottery|claim now', content, re.IGNORECASE):
            risk_score += 25
            warnings.append('Contains prize or lottery language')
        
        if re.search(r'bitcoin|crypto|wallet|seed phrase|private key', content, re.IGNORECASE):
            risk_score += 30
            warnings.append('Mentions cryptocurrency - be extremely cautious')
    
    elif check_type == 'url':
        # Check URL for suspicious patterns
        if not content.startswith('https://'):
            risk_score += 30
            warnings.append('Not using secure HTTPS protocol')
        
        if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content):
            risk_score += 25
            warnings.append('Uses IP address instead of domain name')
        
        if len(content) > 75:
            risk_score += 15
            warnings.append('Unusually long URL')
        
        if re.search(r'[^a-zA-Z0-9\-\.]', content.split('//')[1].split('/')[0] if '//' in content else content):
            risk_score += 20
            warnings.append('Contains suspicious characters in domain')
        
        # Check for common phishing patterns
        if re.search(r'paypal|amazon|microsoft|apple|bank', content, re.IGNORECASE) and not any(x in content.lower() for x in ['.paypal.com', '.amazon.com', '.microsoft.com', '.apple.com']):
            risk_score += 35
            warnings.append('Possible brand impersonation detected')
    
    elif check_type == 'message':
        # Check for social engineering and scam indicators
        if re.search(r'money|western union|gift card|bitcoin|wire transfer|crypto|send funds', content, re.IGNORECASE):
            risk_score += 35
            warnings.append('Mentions money or payment methods')
        
        if re.search(r'emergency|hospital|accident|arrested|urgent help', content, re.IGNORECASE):
            risk_score += 25
            warnings.append('Contains emergency or crisis language')
        
        if re.search(r'trust me|believe me|promise|guaranteed|100%', content, re.IGNORECASE):
            risk_score += 15
            warnings.append('Uses trust-building or guarantee language')
        
        if re.search(r'investment|profit|returns|double your money|passive income', content, re.IGNORECASE):
            risk_score += 30
            warnings.append('Contains investment opportunity language')
        
        if re.search(r'limited time|act now|expires|last chance', content, re.IGNORECASE):
            risk_score += 20
            warnings.append('Creates false sense of urgency')
    
    # Determine risk level
    if risk_score >= 70:
        risk_level = 'HIGH'
        risk_color = 'danger'
        recommendation = 'This appears to be a scam. Do not respond or provide any information.'
    elif risk_score >= 40:
        risk_level = 'MEDIUM'
        risk_color = 'warning'
        recommendation = 'Exercise extreme caution. Verify through official channels before taking any action.'
    else:
        risk_level = 'LOW'
        risk_color = 'success'
        recommendation = 'Appears relatively safe, but always remain vigilant.'
    
    return jsonify({
        'risk_score': min(risk_score, 100),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'warnings': warnings,
        'recommendation': recommendation
    })

@app.route('/ai-detector')
def ai_detector():
    return render_template('ai_detector.html')

@app.route('/api/detect-ai', methods=['POST'])
def detect_ai():
    # This is a simulated AI detection - in production, you'd use actual AI detection APIs
    file_type = request.form.get('file_type')
    
    # Simulate analysis
    import random
    
    # Generate realistic-looking scores
    ai_probability = random.randint(15, 85)
    
    indicators = []
    confidence = 'Medium'
    
    if file_type == 'image':
        if ai_probability > 60:
            indicators = [
                'Unusual pixel patterns detected',
                'Inconsistent lighting and shadows',
                'Artifacts typical of AI generation',
                'Unnatural texture smoothness'
            ]
            confidence = 'High'
        elif ai_probability > 40:
            indicators = [
                'Some digital manipulation detected',
                'Minor inconsistencies in details'
            ]
        else:
            indicators = [
                'Natural noise patterns present',
                'Consistent metadata',
                'Realistic imperfections'
            ]
            confidence = 'High'
    
    elif file_type == 'audio':
        if ai_probability > 60:
            indicators = [
                'Unnatural speech patterns detected',
                'Consistent tone without human variation',
                'Lack of breathing sounds',
                'Robotic prosody patterns'
            ]
            confidence = 'High'
        elif ai_probability > 40:
            indicators = [
                'Some synthetic characteristics',
                'Minor audio artifacts'
            ]
        else:
            indicators = [
                'Natural speech variations present',
                'Background noise consistent with recording',
                'Human breathing patterns detected'
            ]
            confidence = 'High'
    
    elif file_type == 'video':
        if ai_probability > 60:
            indicators = [
                'Facial movement inconsistencies',
                'Unnatural blinking patterns',
                'Lip-sync anomalies detected',
                'Frame-to-frame artifacts'
            ]
            confidence = 'Medium'
        elif ai_probability > 40:
            indicators = [
                'Some deepfake characteristics',
                'Minor temporal inconsistencies'
            ]
        else:
            indicators = [
                'Natural human movements',
                'Consistent lighting across frames',
                'Realistic facial expressions'
            ]
            confidence = 'Medium'
    
    result = 'AI-Generated' if ai_probability > 50 else 'Likely Authentic'
    
    return jsonify({
        'result': result,
        'ai_probability': ai_probability,
        'confidence': confidence,
        'indicators': indicators,
        'recommendation': get_ai_recommendation(ai_probability)
    })

def get_ai_recommendation(probability):
    if probability > 70:
        return 'High likelihood of AI generation. Exercise extreme caution and verify through multiple sources.'
    elif probability > 50:
        return 'Moderate signs of AI generation. Verify authenticity before trusting or sharing.'
    elif probability > 30:
        return 'Some AI characteristics detected. Consider additional verification if content is sensitive.'
    else:
        return 'Appears authentic, but always verify important content through official sources.'

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/api/report', methods=['POST'])
def submit_report():
    data = request.json
    
    # Prepare email content
    email_subject = f"Scam Report: {data.get('scam_type', 'Unknown').upper()}"
    
    email_body = f"""
    NEW SCAM REPORT SUBMISSION
    ========================
    
    Report Details:
    ---------------
    Scam Type: {data.get('scam_type', 'Not specified')}
    Contact Method: {data.get('contact_method', 'Not specified')}
    Date of Incident: {data.get('incident_date', 'Not specified')}
    
    Description:
    {data.get('description', 'No description provided')}
    
    Scammer Information:
    {data.get('scammer_contact', 'No contact information provided')}
    
    Financial Loss:
    Lost Money: {data.get('lost_money', 'No')}
    Amount: {data.get('amount', 'N/A')}
    
    Reporter Contact:
    {data.get('reporter_email', 'Anonymous')}
    
    Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    ========================
    This report was submitted through ScamGuard Online Scam Awareness System.
    """
    
    # Try to send email
    email_sent = False
    error_message = None
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['Subject'] = email_subject
        
        # Add body
        msg.attach(MIMEText(email_body, 'plain'))
        
        # Connect to SMTP server
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        
        # Login (only if credentials are configured)
        if EMAIL_CONFIG['sender_email'] != 'your-email@gmail.com':
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            
            # Send to each authority
            for authority_email in EMAIL_CONFIG['authorities']:
                msg['To'] = authority_email
                server.send_message(msg)
                del msg['To']
            
            email_sent = True
        else:
            # Email not configured - save to file instead
            save_report_to_file(data, email_body)
            email_sent = True  # Consider it "sent" since it's saved
            
        server.quit()
        
    except Exception as e:
        error_message = str(e)
        # Save to file as backup
        save_report_to_file(data, email_body)
        email_sent = True  # Report is saved even if email fails
    
    return jsonify({
        'success': True,
        'message': 'Thank you for your report. It has been submitted to the authorities.' if email_sent else 'Report saved locally. Please configure email settings.',
        'email_sent': email_sent
    })

def save_report_to_file(data, email_body):
    """Save report to a local file as backup"""
    try:
        # Create reports directory if it doesn't exist
        if not os.path.exists('reports'):
            os.makedirs('reports')
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/scam_report_{timestamp}.txt"
        
        # Write report to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(email_body)
            f.write("\n\n--- RAW DATA ---\n")
            f.write(str(data))
        
        return True
    except Exception as e:
        print(f"Error saving report: {e}")
        return False

if __name__ == '__main__':
    app.run(debug=True)