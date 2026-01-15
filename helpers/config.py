"""Module for general configurations of the process"""

import os

MAX_RETRY = 10

# ----------------------
# Queue population settings
# ----------------------
MAX_CONCURRENCY = 100  # tune based on backend capacity
MAX_RETRIES = 3  # transient failure retries per item
RETRY_BASE_DELAY = 0.5  # seconds (exponential backoff)

# Sharepoint Site URL & Document library --> Same across all sites
SHAREPOINT_SITE_URL = "https://aarhuskommune.sharepoint.com/"
DOCUMENT_LIBRARY = "Delte dokumenter"

# Digi Lederteam SHAREPOINT stuff
# ----------------
DIGILEDERTEAM_SHAREPOINT_SITE_NAME = "Digilederteam-Boldbanen/"

DIGILEDERTEAM_SHAREPOINT_KWARGS = {
    "tenant": os.getenv("TENANT"),
    "client_id": os.getenv("CLIENT_ID"),
    "thumbprint": os.getenv("APPREG_THUMBPRINT"),
    "cert_path": os.getenv("GRAPH_CERT_PEM"),
    "site_url": f"{SHAREPOINT_SITE_URL}",
    "site_name": f"{DIGILEDERTEAM_SHAREPOINT_SITE_NAME}",
    "document_library": f"{DOCUMENT_LIBRARY}",
}

# DigiDaglig SHAREPOINT stuff
# ----------------
DIGIDAGLIG_SHAREPOINT_SITE_NAME = "tea-teamsite11325/"

DIGIDAGLIG_SHAREPOINT_KWARGS = {
    "tenant": os.getenv("TENANT"),
    "client_id": os.getenv("CLIENT_ID"),
    "thumbprint": os.getenv("APPREG_THUMBPRINT"),
    "cert_path": os.getenv("GRAPH_CERT_PEM"),
    "site_url": f"{SHAREPOINT_SITE_URL}",
    "site_name": f"{DIGIDAGLIG_SHAREPOINT_SITE_NAME}",
    "document_library": f"{DOCUMENT_LIBRARY}",
}
