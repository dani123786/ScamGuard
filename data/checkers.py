import re


# --- Shared patterns used by both email and message checks ---

URGENCY_PATTERN = re.compile(
    r'urgent|act now|verify|suspended|locked|immediate action|respond immediately|'
    r'within 24 hours|within 48 hours|don\'t delay|time sensitive|asap|right away|'
    r'before it\'s too late|expires soon|last chance|limited time|act immediately|'
    r'immediately|payment required|pay immediately|pay now|due immediately|'
    r'overdue|past due|final notice|final warning|account will be|action required',
    re.IGNORECASE
)

MONEY_PATTERN = re.compile(
    r'send money|wire transfer|western union|gift card|bitcoin|crypto|'
    r'transfer funds|bank transfer|moneygram|zelle|cashapp|venmo|paypal me|'
    r'send funds|financial help|need money|money urgently|pay now|payment required|'
    r'send \$|transfer \$|deposit now|kindly pay|please pay|make payment|'
    r'invoice|overdue|amount due|balance due|payment link|pay via|pay using',
    re.IGNORECASE
)

SENSITIVE_INFO_PATTERN = re.compile(
    r'password|ssn|social security|credit card|bank account|card number|'
    r'cvv|pin number|account details|verify your account|confirm your identity|'
    r'date of birth|mother\'s maiden|security question|private key|seed phrase|'
    r'login credentials|username and password',
    re.IGNORECASE
)

PRIZE_PATTERN = re.compile(
    r'congratulations|you have won|winner|prize|lottery|claim now|claim your|'
    r'selected as|lucky winner|reward waiting|free gift|you\'ve been chosen|'
    r'jackpot|sweepstakes|raffle',
    re.IGNORECASE
)

CRYPTO_PATTERN = re.compile(
    r'bitcoin|ethereum|crypto|wallet address|seed phrase|private key|'
    r'nft|binance|coinbase|blockchain transfer|crypto investment|'
    r'double your crypto|send btc|send eth',
    re.IGNORECASE
)

INVESTMENT_PATTERN = re.compile(
    r'investment opportunity|guaranteed returns|double your money|passive income|'
    r'risk free|high returns|profit guaranteed|financial freedom|make money fast|'
    r'get rich|earn from home|100% profit|no risk investment|forex|trading signal|'
    r'insider tip|stock tip',
    re.IGNORECASE
)

EMERGENCY_PATTERN = re.compile(
    r'emergency|hospital|accident|arrested|in trouble|need your help|'
    r'stranded|stuck abroad|mugged|robbed|life or death|critical situation|'
    r'please help me|desperate|in danger',
    re.IGNORECASE
)

TRUST_PATTERN = re.compile(
    r'trust me|believe me|i promise|guaranteed|100%|no risk|completely safe|'
    r'i swear|honest offer|legitimate|verified|certified|official|authorised',
    re.IGNORECASE
)

IMPERSONATION_PATTERN = re.compile(
    r'irs|fbi|cia|microsoft support|apple support|amazon support|paypal support|'
    r'bank of america|your bank|government official|tax authority|social security administration|'
    r'tech support|windows support|virus detected|your computer|your account has been',
    re.IGNORECASE
)

PHISHING_ACTION_PATTERN = re.compile(
    r'click here|click the link|click below|download now|open attachment|'
    r'verify account|confirm identity|update your information|log in here|'
    r'sign in to verify|follow this link|tap here|link below|use the link|'
    r'via the link|through the link|http://|payment link|pay here',
    re.IGNORECASE
)


def check_email(content):
    risk_score = 0
    warnings = []
    signals = 0  # track number of distinct signals for boost

    if URGENCY_PATTERN.search(content):
        risk_score += 20
        warnings.append('Contains urgent or threatening language')
        signals += 1

    if PHISHING_ACTION_PATTERN.search(content):
        risk_score += 20
        warnings.append('Contains suspicious call-to-action')
        signals += 1

    if SENSITIVE_INFO_PATTERN.search(content):
        risk_score += 30
        warnings.append('Requests sensitive personal or financial information')
        signals += 1

    if PRIZE_PATTERN.search(content):
        risk_score += 25
        warnings.append('Contains prize or lottery language')
        signals += 1

    if CRYPTO_PATTERN.search(content):
        risk_score += 30
        warnings.append('Mentions cryptocurrency — be extremely cautious')
        signals += 1

    if IMPERSONATION_PATTERN.search(content):
        risk_score += 35
        warnings.append('Possible impersonation of a trusted organisation')
        signals += 1

    if MONEY_PATTERN.search(content):
        risk_score += 25
        warnings.append('Mentions money transfer or payment methods')
        signals += 1

    if INVESTMENT_PATTERN.search(content):
        risk_score += 25
        warnings.append('Contains investment opportunity language')
        signals += 1

    # Boost: multiple weak signals together are a strong indicator
    if signals >= 3:
        risk_score += 15
        warnings.append('Multiple scam indicators detected together')

    return risk_score, warnings


def check_message(content):
    risk_score = 0
    warnings = []
    signals = 0

    if MONEY_PATTERN.search(content):
        risk_score += 30
        warnings.append('Mentions money transfer or payment methods')
        signals += 1

    if EMERGENCY_PATTERN.search(content):
        risk_score += 25
        warnings.append('Contains emergency or crisis language')
        signals += 1

    if TRUST_PATTERN.search(content):
        risk_score += 20
        warnings.append('Uses trust-building or guarantee language')
        signals += 1

    if INVESTMENT_PATTERN.search(content):
        risk_score += 30
        warnings.append('Contains investment opportunity language')
        signals += 1

    if URGENCY_PATTERN.search(content):
        risk_score += 20
        warnings.append('Creates a false sense of urgency')
        signals += 1

    if CRYPTO_PATTERN.search(content):
        risk_score += 30
        warnings.append('Mentions cryptocurrency — be extremely cautious')
        signals += 1

    if PRIZE_PATTERN.search(content):
        risk_score += 25
        warnings.append('Contains prize or lottery language')
        signals += 1

    if IMPERSONATION_PATTERN.search(content):
        risk_score += 35
        warnings.append('Possible impersonation of a trusted organisation')
        signals += 1

    if SENSITIVE_INFO_PATTERN.search(content):
        risk_score += 30
        warnings.append('Requests sensitive personal or financial information')
        signals += 1

    # Boost: multiple weak signals together are a strong indicator
    if signals >= 3:
        risk_score += 15
        warnings.append('Multiple scam indicators detected together')

    return risk_score, warnings


def evaluate_risk(risk_score, warnings):
    risk_score = min(risk_score, 100)

    if risk_score >= 55:
        risk_level = 'HIGH'
        risk_color = 'danger'
        recommendation = 'This appears to be a scam. Do not respond or provide any information.'
    elif risk_score >= 25:
        risk_level = 'MEDIUM'
        risk_color = 'warning'
        recommendation = 'Exercise extreme caution. Verify through official channels before taking any action.'
    else:
        risk_level = 'LOW'
        risk_color = 'success'
        recommendation = 'Appears relatively safe, but always remain vigilant.'

    return {
        'risk_score': risk_score,
        'risk_level': risk_level,
        'risk_color': risk_color,
        'warnings': warnings,
        'recommendation': recommendation
    }