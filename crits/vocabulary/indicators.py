from crits.vocabulary.vocab import vocab

class IndicatorTypes(vocab):
    """
    Vocabulary for Indicator Types.
    """


    ADJUST_TOKEN = "Adjust Token"
    API_KEY = "API Key"
    AS_NUMBER = "AS Number"
    AS_NAME = "AS Name"
    BANK_ACCOUNT = "Bank account"
    BITCOIN_ACCOUNT = "Bitcoin account"
    CERTIFICATE_FINGERPRINT = "Certificate Fingerprint"
    CERTIFICATE_NAME = "Certificate Name"
    CHECKSUM_CRC16 = "Checksum CRC16"
    CMD_LINE = "Command Line"
    COMPANY_NAME = "Company name"
    COOKIE_NAME = "Cookie Name"
    COUNTRY = "Country"
    CRX = "CRX"
    DEBUG_PATH = "Debug Path"
    DEBUG_STRING = "Debug String"
    DEST_PORT = "Destination Port"
    DEVICE_IO = "Device IO"
    DOC_FROM_URL = "Document from URL"
    DOMAIN = "URI - Domain Name"
    EMAIL_BOUNDARY = "Email Boundary"
    EMAIL_ADDRESS = "Email - Address"
    EMAIL_CONTENT = "Email - Content"
    EMAIL_FROM = "Email Address From"
    EMAIL_HELO = "Email HELO"
    EMAIL_MESSAGE_ID = "Email Message ID"
    EMAIL_ORIGINATING_IP = "Email Originating IP"
    EMAIL_REPLY_TO = "Email Reply-To"
    EMAIL_SENDER = "Email Address Sender"
    EMAIL_SUBJECT = "Email - Subject"
    EMAIL_X_MAILER = "Email - Xmailer"
    EMAIL_X_ORIGINATING_IP = "Email X-Originating IP"
    FILE_CREATED = "File Created"
    FILE_DELETED = "File Deleted"
    FILE_MOVED = "File Moved"
    FILE_NAME = "Windows - FileName"
    FILE_OPENED = "File Opened"
    FILE_PATH = "Windows - FilePath"
    FILE_READ = "File Read"
    FILE_WRITTEN = "File Written"
    GET_PARAM = "GET Parameter"
    IDS_STREETNAME = "IDS - Streetname"
    IMPHASH = "Hash - IMPHASH"
    MD5 = "Hash - MD5"
    SHA1 = "Hash - SHA1"
    SHA256 = "Hash - SHA256"
    SSDEEP = "Hash - SSDEEP"
    HEX_STRING = "Code - Binary_Code"
    HTML_ID = "HTML ID"
    HTTP_REQUEST = "HTTP Request"
    HTTP_RESP_CODE = "HTTP Response Code"
    IPV4_ADDRESS = "Address - ipv4-addr"
    IPV4_SUBNET = "Address - ipv4-net"
    IPV6_ADDRESS = "IPv6 Address"
    IPV6_SUBNET = "IPv6 Subnet"
    LATITUDE = "Latitude"
    LAUNCH_AGENT = "Launch Agent"
    LOCATION = "Location"
    LONGITUDE = "Longitude"
    MALWARE_NAME = "Antivirus - Streetname"
    MEMORY_ALLOC = "Memory Alloc"
    MEMORY_PROTECT = "Memory Protect"
    MEMORY_READ = "Memory Read"
    MEMORY_WRITTEN = "Memory Written"
    MUTANT_CREATED = "Mutant Created"
    MUTEX = "Windows - Mutex"
    NAME_SERVER = "Name Server"
    OTHER_FILE_OP = "Other File Operation"
    PASSWORD = "Password"
    PASSWORD_SALT = "Password Salt"
    PAYLOAD_DATA = "Payload Data"
    PAYLOAD_TYPE = "Payload Type"
    PIPE = "Pipe"
    POST_DATA = "POST Data"
    PROCESS_NAME = "Process Name"
    PROTOCOL = "Protocol"
    REFERER = "Referer"
    REFERER_OF_REFERER = "Referer of Referer"
    REGISTRAR = "Registrar"
    REGISTRY_KEY = "Windows - Registry"
    REG_KEY_CREATED = "Registry Key Created"
    REG_KEY_DELETED = "Registry Key Deleted"
    REG_KEY_ENUMERATED = "Registry Key Enumerated"
    REG_KEY_MONITORED = "Registry Key Monitored"
    REG_KEY_OPENED = "Registry Key Opened"
    REG_KEY_VALUE_CREATED = "Registry Key Value Created"
    REG_KEY_VALUE_DELETED = "Registry Key Value Deleted"
    REG_KEY_VALUE_MODIFIED = "Registry Key Value Modified"
    REG_KEY_VALUE_QUERIED = "Registry Key Value Queried"
    SERVICE_NAME = "Windows - Service"
    SMS_ORIGIN = "SMS Origin"
    SOURCE_PORT = "Source Port"
    STRING_PE = "String - PE"
    STRING_JS = "String - JS"
    STRING_VBS = "String - VBS"
    STRING_PDF = "String - PDF"
    STRING_RTF = "String - RTF"
    STRING_OFFICE = "String - Office"
    STRING_SWF = "String - SWF"
    STRING_JAVA = "String - Java"
    STRING_EPS = "String - EPS"
    STRING_WIN_SHELL = "String - Windows Shell"
    STRING_UNIX_SHELL = "String - Unix Shell"
    STRING_AUTOIT = "String - AutoIt"
    TELEPHONE = "Telephone"
    TIME_CREATED = "Time Created"
    TIME_UPDATED = "Time Updated"
    TRACKING_ID = "Tracking ID"
    TS_END = "TS End"
    TS_START = "TS Start"
    URI = "URI - URL"
    URI_PATH = "URI - Path"
    USER_AGENT = "URI - HTTP - UserAgent"
    USER_ID = "User ID"
    VICTIM_IP = "Victim IP"
    VOLUME_QUERIED = "Volume Queried"
    WEBSTORAGE_KEY = "Webstorage Key"
    WEB_PAYLOAD = "Web Payload"
    WHOIS_NAME = "WHOIS Name"
    WHOIS_ADDR1 = "WHOIS Address 1"
    WHOIS_ADDR2 = "WHOIS Address 2"
    WHOIS_GENERAL = "Whois"
    WHOIS_TELEPHONE = "WHOIS Telephone"
    XPI = "XPI"


class IndicatorThreatTypes(vocab):
    """
    Vocabulary for Indicator Threat Types.
    """


    BAD_ACTOR = "Bad Actor"
    COMPROMISED_CREDENTIAL = "Compromised Credential"
    COMMAND_EXEC = "Command Exec"
    MALICIOUS_AD = "Malicious Ad"
    MALICIOUS_CONTENT = "Malicious Content"
    MALICIOUS_DOMAIN = "Malicious Domain"
    MALICIOUS_INJECT = "Malicious Inject"
    MALICIOUS_IP = "Malicious IP"
    MALICIOUS_URL = "Malicious URL"
    MALICIOUS_URLCHUNK = "Malicious URL Chunk"
    MALWARE_ARTIFACTS = "Malware Artifacts"
    MALWARE_SAMPLE = "Malware Sample"
    MALWARE_VICTIM = "Malware Victim"
    PROXY_IP = "Proxy IP"
    SINKHOLE_EVENT = "Sinkhole Event"
    SMS_SPAM = "SMS Spam"
    UNKNOWN = "Unknown"
    VICTIM_IP_USAGE = "Victim IP Usage"
    WEB_REQUEST = "Web Request"
    WHITELIST_DOMAIN = "Whitelist Domain"
    WHITELIST_IP = "Whitelist IP"
    WHITELIST_URL = "Whitelist URL"


class IndicatorAttackTypes(vocab):
    """
    Vocabulary for Indicator Attack Types.
    """


    ACCESS_TOKEN_THEFT = "Access Token Theft"
    BRUTE_FORCE = "Brute Force"
    CLICKJACKING = "Clickjacking"
    EMAIL_SPAM = "Email Spam"
    FAKE_ACCOUNTS = "Fake Accounts"
    IP_INFRINGEMENT = "IP Infringement"
    MALICIOUS_APP = "Malicious App"
    MALWARE = "Malware"
    PHISHING = "Phishing"
    SELF_XSS = "Self XSS"
    SHARE_BAITING = "Share Baiting"
    TARGETED = "Targeted"
    UNKNOWN = "Unknown"


class IndicatorCI(vocab):
    """
    Vocabulary for Indicator CI.
    """


    UNKNOWN = "unknown"
    BENIGN = "benign"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
