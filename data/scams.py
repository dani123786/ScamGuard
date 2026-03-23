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