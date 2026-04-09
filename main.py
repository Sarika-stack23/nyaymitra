# ============================================================
# NYAYMITRA — Your Free AI Legal Assistant
# main.py — Complete Single File Application
# Version: 2.0 Final
# ============================================================


# ============================================================
# SECTION 1 — IMPORTS
# ============================================================

import os
import json
import re
import tempfile
import datetime
import traceback
import smtplib
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Load .env file if present (for local dev)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required — can set keys directly

# Groq AI
from groq import Groq

# Voice — Speech to Text
import whisper

# Voice — Text to Speech
from gtts import gTTS

# PDF Generation
from fpdf import FPDF

# Language Detection
from langdetect import detect

# Translation
from deep_translator import GoogleTranslator

# UI
import streamlit as st


# ============================================================
# SECTION 2 — CONFIGURATION
# ============================================================

# --- Email Config (Gmail SMTP) ---
# Set in .env file or GitHub Codespaces Secrets
EMAIL_SENDER   = os.getenv("EMAIL_SENDER",   "your_gmail@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_app_password_here")

# --- Google Maps Base URL ---
GOOGLE_MAPS_URL = "https://www.google.com/maps/search/?api=1&query="

# --- API Key ---
# Set in .env file or GitHub Codespaces Secrets
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")

# --- Groq Client ---
groq_client = Groq(api_key=GROQ_API_KEY)

# --- Groq Model ---
GROQ_MODEL = "llama-3.3-70b-versatile"     # Best free model on Groq (2025)

# --- Whisper Model ---
WHISPER_MODEL_SIZE = "base"                 # tiny | base | small | medium

# --- Supported Languages ---
SUPPORTED_LANGUAGES = {
    "English":  "en",
    "Hindi":    "hi",
    "Kannada":  "kn",
    "Tamil":    "ta",
    "Telugu":   "te",
}

# --- Legal Domains ---
LEGAL_DOMAINS = ["tenant", "labor", "consumer", "family", "rti", "fir"]

# --- Office Addresses by Domain and District ---
OFFICE_ADDRESSES = {
    "labor": {
        "Bengaluru":  "Labour Commissioner Office, Kanakapura Road, Bengaluru - 560029",
        "Mysuru":     "Labour Commissioner Office, JLB Road, Mysuru - 570005",
        "Tumakuru":   "Labour Commissioner Office, B.H. Road, Tumakuru - 572101",
        "Kanakapura": "Labour Commissioner Office, Kanakapura Road, Bengaluru - 560029",
        "Mangaluru":  "Labour Commissioner Office, Lalbagh, Mangaluru - 575001",
        "Hubballi":   "Labour Commissioner Office, Hubballi - 580029",
        "default":    "Your nearest District Labour Commissioner Office",
    },
    "consumer": {
        "Bengaluru":  "District Consumer Disputes Redressal Commission, Richmond Road, Bengaluru - 560025",
        "Mysuru":     "District Consumer Forum, Mysuru - 570001",
        "Tumakuru":   "District Consumer Forum, Tumakuru - 572101",
        "Kanakapura": "District Consumer Forum, Kanakapura - 562117",
        "Mangaluru":  "District Consumer Forum, Mangaluru - 575001",
        "Hubballi":   "District Consumer Forum, Hubballi - 580029",
        "default":    "Your nearest District Consumer Disputes Redressal Commission",
    },
    "tenant": {
        "Bengaluru":  "Rent Control Court, K.G. Road, Bengaluru - 560009",
        "Mysuru":     "Rent Control Court, Mysuru - 570001",
        "Kanakapura": "Civil Court, Kanakapura - 562117",
        "Mangaluru":  "Civil Court, Mangaluru - 575001",
        "Hubballi":   "Civil Court, Hubballi - 580029",
        "default":    "Your nearest Civil Court or Rent Control Court",
    },
    "family": {
        "Bengaluru":  "Family Court, Annasandrapalya, Bengaluru - 560047",
        "Mysuru":     "Family Court, Mysuru - 570001",
        "Kanakapura": "Civil Court, Kanakapura - 562117",
        "default":    "Your nearest Family Court",
    },
    "rti": {
        "Bengaluru":  "Karnataka Information Commission, Bengaluru - 560001",
        "default":    "Public Information Officer (PIO) of the concerned government department",
    },
    "fir": {
        "Bengaluru":  "Your nearest Police Station — or file online at ksp.karnataka.gov.in",
        "Kanakapura": "Kanakapura Police Station, Kanakapura - 562117",
        "default":    "Your nearest Police Station",
    },
}

# --- Session Flow Steps ---
STEPS = [
    "GREETING",
    "PROBLEM_COLLECTION",
    "RIGHTS_EXPLAINED",
    "DETAILS_COLLECTION",
    "DOCUMENT_GENERATED",
    "ACTION_GUIDE_GIVEN",
    "COMPLETED",
]

# --- Required Details per Domain ---
REQUIRED_DETAILS = {
    "labor": [
        "user_name",
        "contractor_name",
        "contractor_address",
        "work_start_date",
        "work_end_date",
        "amount_pending",
        "user_district",
    ],
    "tenant": [
        "user_name",
        "landlord_name",
        "landlord_address",
        "property_address",
        "deposit_amount",
        "tenancy_end_date",
        "user_district",
    ],
    "consumer": [
        "user_name",
        "company_name",
        "company_address",
        "product_or_service",
        "amount_paid",
        "date_of_purchase",
        "issue_description",
        "user_district",
    ],
    "family": [
        "user_name",
        "spouse_name",
        "marriage_date",
        "issue_description",
        "user_district",
    ],
    "rti": [
        "user_name",
        "department_name",
        "department_address",
        "information_requested",
        "user_district",
    ],
    "fir": [
        "user_name",
        "incident_description",
        "incident_date",
        "accused_name",
        "accused_address",
        "user_district",
    ],
}

# --- Friendly Question Labels ---
DETAIL_LABELS = {
    "user_name":          "your full name",
    "contractor_name":    "the contractor or employer's full name",
    "contractor_address": "the contractor or employer's full address",
    "work_start_date":    "the date you started working (e.g. January 2024)",
    "work_end_date":      "the date you stopped working or the project ended",
    "amount_pending":     "the total unpaid amount in Rupees",
    "user_district":      "your city or district name (e.g. Bengaluru, Kanakapura)",
    "landlord_name":      "your landlord's full name",
    "landlord_address":   "your landlord's full address",
    "property_address":   "the full address of the rented property",
    "deposit_amount":     "the security deposit amount in Rupees",
    "tenancy_end_date":   "the date you vacated the property",
    "company_name":       "the company or seller's full name",
    "company_address":    "the company or seller's full address",
    "product_or_service": "the name of the product or service you purchased",
    "amount_paid":        "the total amount you paid in Rupees",
    "date_of_purchase":   "the date you made the purchase",
    "issue_description":  "a short description of the problem (e.g. product was defective)",
    # Family
    "spouse_name":        "your spouse's full name",
    "marriage_date":      "your date of marriage",
    # RTI
    "department_name":    "the name of the government department or office",
    "department_address": "the address of that government office",
    "information_requested": "exactly what information or documents you want from the government",
    # FIR
    "incident_description": "what happened — describe the incident clearly",
    "incident_date":      "the date the incident happened",
    "accused_name":       "the name of the person who did this (if known)",
    "accused_address":    "the address of that person (if known — write 'unknown' if not)",
}


# ============================================================
# SECTION 3 — LEGAL KNOWLEDGE BASE
# ============================================================

LEGAL_KNOWLEDGE = {

    "labor": {
        "law_name": "Payment of Wages Act, 1936 & Minimum Wages Act, 1948",
        "key_rights": [
            "You must be paid on time every month — by the 7th of the following month",
            "You cannot be paid less than the government minimum wage",
            "Employer cannot make any illegal deductions from your salary",
            "You can file a complaint with the Labour Commissioner completely free",
            "You can claim up to 3 years of unpaid wages",
            "The employer can be fined and penalized under Indian law for non-payment",
            "You do not need a lawyer — you can do this yourself",
        ],
        "documents_needed": [
            "Legal Notice to Employer / Contractor",
            "Labour Complaint Letter to Labour Commissioner",
        ],
        "time_limit":      "3 years from date of non-payment",
        "cost":            "Free — no lawyer or court fee needed",
        "resolution_time": "Usually 30 to 90 days",
    },

    "tenant": {
        "law_name": "Transfer of Property Act & Karnataka Rent Control Act",
        "key_rights": [
            "Landlord must return your full security deposit after you vacate",
            "Landlord cannot evict you without giving 1 to 3 months written notice",
            "Landlord cannot enter your rented home without your permission",
            "Landlord must give you a written receipt for every rent payment",
            "You can challenge illegal eviction in the Rent Control Court",
            "You can deduct cost of repairs from rent if landlord refuses to fix issues",
            "You do not need a lawyer — you can approach the court yourself",
        ],
        "documents_needed": [
            "Legal Notice to Landlord",
            "Complaint to Rent Control Court or Civil Court",
        ],
        "time_limit":      "File within 1 year of the incident",
        "cost":            "Free or very low court fee",
        "resolution_time": "Usually 30 to 60 days for deposit recovery",
    },

    "consumer": {
        "law_name": "Consumer Protection Act, 2019",
        "key_rights": [
            "You have the right to a full refund for any defective product",
            "You have the right to compensation for poor or incomplete service",
            "You can file a complaint against online sellers like Amazon, Flipkart etc.",
            "Filing a consumer complaint is completely free for claims up to Rs. 5 lakh",
            "You can also claim compensation for mental stress and harassment",
            "The company must respond to your complaint within 30 days",
            "You can file the complaint online at consumerhelpline.gov.in",
        ],
        "documents_needed": [
            "Consumer Complaint Letter to District Consumer Commission",
            "Demand Notice to the Company",
        ],
        "time_limit":      "2 years from the date of purchase or service",
        "cost":            "Free for claims up to Rs. 5 lakh",
        "resolution_time": "Usually 45 to 90 days",
    },

    "family": {
        "law_name": "Hindu Marriage Act, 1955 & Protection of Women from Domestic Violence Act, 2005",
        "key_rights": [
            "Wife has the right to maintenance from husband under Section 125 CrPC",
            "You can file for divorce on grounds of cruelty, desertion, or adultery",
            "Women have the right to live in the shared household — husband cannot throw you out",
            "You can get a Protection Order against domestic violence for free",
            "Children's custody can be decided by the Family Court in the child's best interest",
            "You can claim alimony and maintenance during and after divorce proceedings",
            "Filing a domestic violence complaint is free and police must act on it",
        ],
        "documents_needed": [
            "Domestic Violence Complaint to Magistrate",
            "Application for Maintenance under Section 125 CrPC",
        ],
        "time_limit":      "File as soon as possible — no fixed limit for domestic violence",
        "cost":            "Free — legal aid available at District Legal Services Authority",
        "resolution_time": "Protection order within 3 days; maintenance within 60 days",
    },

    "rti": {
        "law_name": "Right to Information Act, 2005",
        "key_rights": [
            "Every Indian citizen has the right to get information from any government office",
            "Government must reply to your RTI within 30 days",
            "You can ask for documents, records, files, or any government data",
            "RTI application fee is only Rs. 10",
            "If government does not reply in 30 days, you can file a First Appeal",
            "If First Appeal fails, you can go to the Information Commission",
            "You can file RTI online at rtionline.gov.in completely free",
        ],
        "documents_needed": [
            "RTI Application Letter to Public Information Officer",
        ],
        "time_limit":      "No time limit — you can file anytime",
        "cost":            "Rs. 10 application fee only",
        "resolution_time": "Government must reply within 30 days",
    },

    "fir": {
        "law_name": "Code of Criminal Procedure (CrPC), 1973",
        "key_rights": [
            "Every person has the right to file an FIR at any police station for free",
            "Police cannot refuse to register an FIR for a cognizable offence",
            "You can file a Zero FIR at any police station — not just where the crime happened",
            "If police refuse to file FIR, you can complain directly to the Superintendent of Police",
            "You have the right to get a free copy of your FIR",
            "You can also file an FIR online at your state police website",
            "If police still refuse, you can file a complaint before the Magistrate under Section 156(3)",
        ],
        "documents_needed": [
            "FIR Complaint Letter to Police Station",
            "Written Complaint to Superintendent of Police (if police refuse)",
        ],
        "time_limit":      "File as soon as possible after the incident",
        "cost":            "Completely free",
        "resolution_time": "FIR must be registered immediately — investigation within 60-90 days",
    },
}


# ============================================================
# SECTION 4 — DOCUMENT TEMPLATES
# ============================================================

DOCUMENT_TEMPLATES = {

    "legal_notice_labor": """
LEGAL NOTICE

Date: {date}

To,
{contractor_name}
{contractor_address}

Subject: Legal Notice for Non-Payment of Wages under the Payment of Wages Act, 1936

Sir / Madam,

I, {user_name}, hereby serve upon you this legal notice.

I was employed under your supervision from {work_start_date} to {work_end_date}.
Despite completing all my duties faithfully during this period, you have failed
and neglected to pay my wages amounting to Rs. {amount_pending}/-.

This is a clear violation of the Payment of Wages Act, 1936, which makes it
mandatory for every employer to pay wages within the prescribed time.

You are hereby called upon to pay the outstanding amount of Rs. {amount_pending}/-
within 15 (fifteen) days from the date of receipt of this notice.

Failing which, I shall be left with no option but to:
1. File a formal complaint before the Labour Commissioner, {user_district}
2. Initiate appropriate legal proceedings against you
3. Claim interest and additional compensation as permitted under law

All costs and consequences of such action shall be borne entirely by you.

Yours faithfully,
{user_name}
Date: {date}
""",

    "labour_complaint": """
To,
The Labour Commissioner
{user_district}

Date: {date}

Subject: Complaint for Non-Payment of Wages against {contractor_name}
         Under the Payment of Wages Act, 1936

Respected Sir / Madam,

I, {user_name}, humbly wish to bring the following complaint to your kind attention.

1. I was employed by {contractor_name}, address: {contractor_address}
2. My employment period: {work_start_date} to {work_end_date}
3. Amount of wages unpaid: Rs. {amount_pending}/-
4. Despite completing all work sincerely, the employer has refused to pay my dues.
5. Repeated verbal and written requests have been ignored by the employer.

The employer has clearly violated the Payment of Wages Act, 1936.

I humbly request your good office to:
1. Investigate this matter at the earliest
2. Direct the employer to pay the full amount of Rs. {amount_pending}/- immediately
3. Take appropriate legal action against the employer under relevant provisions

I am enclosing a copy of the legal notice sent to the employer for your reference.

Thanking you,
Yours faithfully,
{user_name}
Date: {date}
""",

    "legal_notice_tenant": """
LEGAL NOTICE

Date: {date}

To,
{landlord_name}
{landlord_address}

Subject: Legal Notice for Non-Return of Security Deposit

Sir / Madam,

I, {user_name}, hereby serve upon you this legal notice.

I was your tenant residing at {property_address}.
My tenancy came to an end on {tenancy_end_date}, and I vacated the premises
in good and clean condition on the said date.

Despite vacating the property peacefully, you have failed and refused to return
my security deposit of Rs. {deposit_amount}/-.

You are hereby called upon to return the full security deposit of Rs. {deposit_amount}/-
within 15 (fifteen) days from the date of receipt of this notice.

Failing which, I shall be left with no option but to:
1. File a complaint before the Rent Control Court / Civil Court at {user_district}
2. Claim the deposit along with interest and compensation for harassment

All legal costs shall be borne entirely by you.

Yours faithfully,
{user_name}
Date: {date}
""",

    "consumer_complaint": """
To,
The President
District Consumer Disputes Redressal Commission
{user_district}

Date: {date}

Subject: Consumer Complaint against {company_name}
         Under the Consumer Protection Act, 2019

Respected Sir / Madam,

I, {user_name}, humbly file this complaint against {company_name}.

FACTS:
1. I purchased {product_or_service} from {company_name} ({company_address})
2. Date of purchase: {date_of_purchase}
3. Amount paid: Rs. {amount_paid}/-
4. Nature of complaint: {issue_description}

Despite repeated requests, the company has failed to resolve the matter or
provide any satisfactory response. This constitutes deficiency in service and
unfair trade practice under the Consumer Protection Act, 2019.

I respectfully request this Commission to:
1. Direct {company_name} to refund Rs. {amount_paid}/-
2. Award compensation for mental harassment and inconvenience
3. Award litigation costs
4. Pass any other order deemed fit in the interest of justice

I declare that the above facts are true and correct to the best of my knowledge.

Yours faithfully,
{user_name}
Date: {date}
""",

    "demand_notice": """
DEMAND NOTICE

Date: {date}

To,
{company_name}
{company_address}

Subject: Demand for Refund / Complaint Resolution

Sir / Madam,

I, {user_name}, hereby put you on formal notice.

I purchased {product_or_service} from your company on {date_of_purchase}
for Rs. {amount_paid}/-.

Issue: {issue_description}

Despite my repeated follow-ups, you have failed to resolve this issue satisfactorily.

You are hereby called upon to either refund Rs. {amount_paid}/- in full or
resolve this issue within 15 days from receipt of this notice.

Failing which, I will file a consumer complaint before the District Consumer
Disputes Redressal Commission, {user_district} and seek additional compensation
for harassment and legal costs.

Yours faithfully,
{user_name}
Date: {date}
""",

    "domestic_violence_complaint": """
To,
The Hon'ble Judicial Magistrate
{user_district}

Date: {date}

Subject: Application under the Protection of Women from Domestic Violence Act, 2005

Respected Sir / Madam,

I, {user_name}, humbly submit this application against {spouse_name}.

We were married on {marriage_date}.

Details of the domestic violence / issue:
{issue_description}

I hereby request this Hon'ble Court to:
1. Issue a Protection Order restraining the respondent from committing further acts of violence
2. Grant residence order allowing me to continue living in the shared household
3. Award monetary relief and maintenance as deemed appropriate
4. Pass any other order in the interest of justice and my safety

I am ready to provide further evidence and appear before this Court as directed.

Yours faithfully,
{user_name}
Date: {date}
""",

    "rti_application": """
To,
The Public Information Officer
{department_name}
{department_address}

Date: {date}

Subject: Application under the Right to Information Act, 2005

Sir / Madam,

I, {user_name}, a citizen of India, hereby request the following information
under Section 6(1) of the Right to Information Act, 2005.

Information Required:
{information_requested}

I am enclosing an application fee of Rs. 10/- (Rupees Ten only) by Indian Postal Order
/ Demand Draft / Cash (as applicable).

I request you to provide the above information within 30 days as required under
Section 7(1) of the RTI Act, 2005.

If the information requested is not available with your office, kindly transfer this
application to the concerned Public Authority under Section 6(3) of the RTI Act.

Yours faithfully,
{user_name}
District: {user_district}
Date: {date}
""",

    "fir_complaint": """
To,
The Station House Officer
{user_district} Police Station

Date: {date}

Subject: Complaint for Registration of FIR

Respected Sir / Madam,

I, {user_name}, a resident of {user_district}, wish to register a complaint
against {accused_name} ({accused_address}).

Details of the Incident:

Date of Incident: {incident_date}

What Happened:
{incident_description}

I humbly request you to:
1. Register an FIR against the accused immediately
2. Investigate the matter thoroughly
3. Take appropriate legal action against the accused
4. Provide me a free copy of the FIR as per my legal right

I am willing to cooperate fully with the investigation.

Yours faithfully,
{user_name}
Date: {date}
""",
}


# ============================================================
# SECTION 5 — AI PROMPTS
# ============================================================

PROMPTS = {

    "classify_domain": """
You are a legal domain classifier for Indian law.
The user will describe their legal problem in any language.
Read the problem carefully and identify which legal domain it falls under.
Reply with ONLY one word from: tenant, labor, consumer, family, rti, fir.
Do not write anything else. No explanation. No punctuation. Just one word.

- tenant  : landlord issues, rent, eviction, security deposit
- labor   : unpaid wages, salary, employer, contractor, job
- consumer: product defect, service complaint, refund, online shopping fraud
- family  : marriage, divorce, domestic violence, maintenance, custody
- rti     : government information, RTI application, government records
- fir     : police complaint, crime, theft, assault, harassment, fraud by person

User problem: {user_problem}
""",

    "explain_rights": """
You are NyayMitra, a warm and caring Indian legal assistant who helps common people.
Your job is to explain the user's legal rights in very simple, easy-to-understand language.

Rules:
- Use very short, clear sentences
- Absolutely no legal jargon
- Be warm, supportive, and empowering
- Tell them clearly that they have rights and they can fight back
- Speak in {language} language only
- Keep response under 180 words total

Information to use:
- Legal domain: {domain}
- Applicable law: {law_name}
- Key rights: {rights}
- Time limit to act: {time_limit}
- Cost: {cost}

After explaining rights, end your message with exactly this line (translated to {language}):
"I will now ask you a few simple questions to prepare your legal documents."
""",

    "ask_questions": """
You are NyayMitra, a friendly Indian legal assistant.
You are collecting information from the user one step at a time to prepare their legal documents.

Strict rules:
- Ask ONLY ONE question at a time — never more than one
- Use very simple, everyday {language} language
- Be warm, patient, and encouraging
- Do not repeat information already collected

Details already collected:
{collected_details}

The next piece of information you need:
Field name: {next_field}
What it means: {next_field_label}

Write one simple, friendly question to ask the user for this information.
Nothing else — just the question.
""",

    "fill_document": """
You are a precise legal document assistant for India.
Your job is to fill in a document template using the provided user details.
Replace every placeholder (like {{user_name}}, {{date}} etc.) with the actual values.
Return ONLY the completed, filled document — no explanations, no extra text.

Template to fill:
{template}

User details to use:
{user_details}

Today's date: {date}
""",

    "action_guide": """
You are NyayMitra, a warm and caring Indian legal assistant.
Write a clear, numbered, step-by-step action guide for the user so they know exactly what to do.

Rules:
- Use simple {language} language only
- Number every step clearly: Step 1, Step 2, etc.
- Be very specific — tell them exactly what to do, where to go, what to carry, what to say
- Be encouraging and supportive throughout
- Keep under 220 words

Context:
- Legal domain: {domain}
- User's district / city: {user_district}
- Office they need to visit: {office_address}
- Expected time to resolve: {resolution_time}

Your guide must include:
1. What to do first (e.g. send the legal notice)
2. Exact list of documents to carry
3. Exact office address to visit
4. What to say or do at the office
5. Realistic expected timeline
6. One final short encouraging sentence
""",

    "general_answer": """
You are NyayMitra, a friendly and knowledgeable Indian legal assistant.
Answer the user's question clearly and helpfully.
Use simple, easy-to-understand {language} language.
Be warm and concise — keep the answer under 150 words.
Do not use legal jargon.

User question: {question}
""",
}


# ============================================================
# SECTION 6 — CORE FUNCTIONS
# ============================================================

# ── 6.1 Language Functions ───────────────────────────────────

def detect_language(text):
    """Auto-detect which language the user is writing in."""
    try:
        detected_code = detect(text)
        for name, code in SUPPORTED_LANGUAGES.items():
            if code == detected_code:
                return name
        return "English"
    except Exception:
        return "English"


def translate_to_english(text, source_language):
    """Translate user text to English for AI processing."""
    try:
        code = SUPPORTED_LANGUAGES.get(source_language, "en")
        if code == "en":
            return text
        result = GoogleTranslator(source=code, target="en").translate(text)
        return result if result else text
    except Exception:
        return text


def translate_to_user_language(text, target_language):
    """Translate AI response to the user's language."""
    try:
        code = SUPPORTED_LANGUAGES.get(target_language, "en")
        if code == "en":
            return text
        result = GoogleTranslator(source="en", target=code).translate(text)
        return result if result else text
    except Exception:
        return text


# ── 6.2 AI / Groq Functions ─────────────────────────────────

def call_groq(prompt, system_message=None):
    """Send a prompt to Groq AI and return the text response."""
    try:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[Groq Error] {str(e)}")
        return "I am sorry, I could not process this. Please try again."


def classify_legal_domain(user_problem_english):
    """Classify user problem into: tenant, labor, or consumer."""
    prompt = PROMPTS["classify_domain"].format(user_problem=user_problem_english)
    result = call_groq(prompt).lower().strip()
    for domain in LEGAL_DOMAINS:
        if domain in result:
            return domain
    return "consumer"  # default fallback


def explain_rights(domain, language):
    """Generate a rights explanation for the given domain in user's language."""
    knowledge = LEGAL_KNOWLEDGE[domain]
    rights_text = "\n".join([f"- {r}" for r in knowledge["key_rights"]])
    prompt = PROMPTS["explain_rights"].format(
        language=language,
        domain=domain,
        law_name=knowledge["law_name"],
        rights=rights_text,
        time_limit=knowledge["time_limit"],
        cost=knowledge["cost"],
    )
    return call_groq(prompt)


def ask_next_question(domain, collected_details, language):
    """Ask the next required question to the user."""
    required = REQUIRED_DETAILS[domain]
    pending = [f for f in required if f not in collected_details]

    if not pending:
        return "DETAILS_COMPLETE"

    next_field = pending[0]
    label = DETAIL_LABELS.get(next_field, next_field.replace("_", " "))

    prompt = PROMPTS["ask_questions"].format(
        language=language,
        collected_details=json.dumps(collected_details, indent=2, ensure_ascii=False),
        next_field=next_field,
        next_field_label=label,
    )
    return call_groq(prompt)


def save_user_answer(domain, collected_details, user_answer, language):
    """Save user's answer into the correct field of collected_details."""
    required = REQUIRED_DETAILS[domain]
    pending = [f for f in required if f not in collected_details]

    if not pending:
        return collected_details

    next_field = pending[0]
    english_answer = translate_to_english(user_answer.strip(), language)
    collected_details[next_field] = english_answer
    return collected_details


def answer_general_question(question, language):
    """Answer any general legal question from the user."""
    english_q = translate_to_english(question, language)
    prompt = PROMPTS["general_answer"].format(
        language=language,
        question=english_q,
    )
    return call_groq(prompt)


# ── 6.3 Document Functions ───────────────────────────────────

def get_template_keys(domain):
    """Return the list of document template keys for a domain."""
    return {
        "labor":    ["legal_notice_labor", "labour_complaint"],
        "tenant":   ["legal_notice_tenant"],
        "consumer": ["consumer_complaint", "demand_notice"],
        "family":   ["domestic_violence_complaint"],
        "rti":      ["rti_application"],
        "fir":      ["fir_complaint"],
    }.get(domain, ["consumer_complaint"])


def fill_all_documents(domain, user_details):
    """Fill all templates for the domain and return combined document text."""
    keys = get_template_keys(domain)
    today = datetime.date.today().strftime("%d %B %Y")
    user_details["date"] = today

    filled = []
    for key in keys:
        template = DOCUMENT_TEMPLATES.get(key, "")
        prompt = PROMPTS["fill_document"].format(
            template=template,
            user_details=json.dumps(user_details, indent=2, ensure_ascii=False),
            date=today,
        )
        filled.append(call_groq(prompt))

    sep = "\n\n" + "=" * 60 + "\n\n"
    return sep.join(filled)


def generate_pdf(document_text, user_name):
    """Convert document text into a downloadable PDF file."""
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        pdf.set_margins(20, 20, 20)
        pdf.set_font("Arial", size=11)

        for line in document_text.split("\n"):
            safe_line = line.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 7, txt=safe_line, align="L")

        safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", user_name)
        filename = f"NyayMitra_{safe_name}_{datetime.date.today()}.pdf"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        pdf.output(filepath)
        return filepath

    except Exception as e:
        print(f"[PDF Error] {str(e)}")
        return None


def generate_action_guide(domain, user_details, language):
    """Generate a step-by-step action guide for the user."""
    knowledge = LEGAL_KNOWLEDGE[domain]
    user_district = user_details.get("user_district", "your district")
    offices = OFFICE_ADDRESSES.get(domain, {})
    office_address = offices.get(user_district, offices.get("default", "Your nearest district office"))

    prompt = PROMPTS["action_guide"].format(
        language=language,
        domain=domain,
        user_district=user_district,
        office_address=office_address,
        resolution_time=knowledge["resolution_time"],
    )
    return call_groq(prompt)


# ── 6.5 Email Function ──────────────────────────────────────

def send_document_by_email(pdf_path, recipient_email, user_name, domain):
    """Send the generated PDF document to user's email address."""
    try:
        if not pdf_path or not os.path.exists(pdf_path):
            return False, "PDF file not found. Please generate the document first."

        subject = f"NyayMitra — Your Legal Document ({domain.capitalize()} Case)"
        body = f"""Dear {user_name},

Please find attached your legal document prepared by NyayMitra.

This document has been generated based on the information you provided.

What to do next:
1. Print this document
2. Sign where required
3. Send by Registered Post to the concerned party
4. Keep a copy for yourself

Remember — Justice is your right. NyayMitra stands with you.

This is a free service provided by NyayMitra.
---
Note: This document is for informational purposes.
For complex legal matters, please also consult a qualified lawyer.
"""
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(pdf_path)}"
        )
        msg.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())

        return True, f"Document sent successfully to {recipient_email}"

    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Please check Gmail App Password in config."
    except Exception as e:
        print(f"[Email Error] {str(e)}")
        return False, f"Could not send email: {str(e)}"


# ── 6.6 Google Maps Function ─────────────────────────────────

def get_maps_link(domain, user_district):
    """Generate a Google Maps search link for the nearest office."""
    offices = OFFICE_ADDRESSES.get(domain, {})
    office_address = offices.get(user_district, offices.get("default", ""))

    if not office_address:
        return None, "Office address not found."

    # Build Google Maps search URL
    query = urllib.parse.quote(office_address)
    maps_url = f"{GOOGLE_MAPS_URL}{query}"

    return maps_url, office_address


def get_maps_html(domain, user_district):
    """Return a clickable HTML link for the office on Google Maps."""
    maps_url, office_address = get_maps_link(domain, user_district)
    if not maps_url:
        return "Office address not available."
    return f'<a href="{maps_url}" target="_blank">📍 {office_address} — Open in Google Maps</a>'


# ── 6.4 Voice Functions ──────────────────────────────────────

def voice_to_text(audio_filepath):
    """Transcribe a voice recording to text using Whisper."""
    try:
        model = whisper.load_model(WHISPER_MODEL_SIZE)
        result = model.transcribe(audio_filepath)
        return result.get("text", "").strip()
    except Exception as e:
        print(f"[Whisper Error] {str(e)}")
        return ""


def text_to_voice(text, language):
    """Convert text to a voice audio file using gTTS."""
    try:
        code = SUPPORTED_LANGUAGES.get(language, "en")
        tts = gTTS(text=text, lang=code, slow=False)
        filepath = os.path.join(tempfile.gettempdir(), "nyaymitra_reply.mp3")
        tts.save(filepath)
        return filepath
    except Exception as e:
        print(f"[TTS Error] {str(e)}")
        return None


# ============================================================
# SECTION 7 — SESSION MANAGER
# ============================================================

def create_session():
    """Create and return a fresh empty session for a new user."""
    return {
        "step":              "GREETING",
        "language":          "English",
        "domain":            None,
        "collected_details": {},
        "document_text":     None,
        "pdf_path":          None,
        "action_guide":      None,
        "conversation":      [],
        "error_count":       0,
    }


def get_progress_status(session):
    """Return a short user-facing progress status string."""
    step = session.get("step", "GREETING")
    domain = session.get("domain") or ""
    collected = session.get("collected_details", {})

    if step == "GREETING":
        return "👋 Ready to help you..."
    elif step == "PROBLEM_COLLECTION":
        return "📝 Tell me your problem..."
    elif step == "RIGHTS_EXPLAINED":
        return f"⚖️ Domain: {domain.capitalize()} — Explaining your rights..."
    elif step == "DETAILS_COLLECTION":
        required = REQUIRED_DETAILS.get(domain, [])
        done = len([f for f in required if f in collected])
        total = len(required)
        return f"📋 Collecting your details: {done} of {total} done"
    elif step == "DOCUMENT_GENERATED":
        return "📄 Documents ready! Preparing your action plan..."
    elif step == "ACTION_GUIDE_GIVEN":
        return "✅ Complete! Download your document below."
    elif step == "COMPLETED":
        return "✅ Done! Ask me anything else."
    return "..."


# ============================================================
# SECTION 8 — MAIN CHAT LOGIC
# ============================================================

def process_message(user_input, session, selected_language):
    """
    Central brain of NyayMitra.
    Controls the full conversation flow based on session step.

    Returns:
        response      (str)  — AI reply to show the user
        session       (dict) — updated session state
        pdf_path      (str)  — path to PDF file if ready, else None
        document_text (str)  — generated document text if ready, else ""
    """
    session["language"] = selected_language
    language = selected_language
    response = ""

    try:

        # ── STEP 1: GREETING ──────────────────────────────────────
        if session["step"] == "GREETING":
            response = translate_to_user_language(
                "Hello! I am NyayMitra — your free AI legal assistant. "
                "I am here to help you understand your rights and prepare your legal documents for free. "
                "\n\nPlease tell me your problem in your own words. "
                "You can type or speak — use any language you are comfortable with.",
                language
            )
            session["step"] = "PROBLEM_COLLECTION"


        # ── STEP 2: PROBLEM COLLECTION ────────────────────────────
        elif session["step"] == "PROBLEM_COLLECTION":
            if not user_input or not user_input.strip():
                response = translate_to_user_language(
                    "Please tell me your problem. I am listening and I am here to help you.",
                    language
                )
            else:
                # Translate to English and classify domain
                english_problem = translate_to_english(user_input, language)
                domain = classify_legal_domain(english_problem)
                session["domain"] = domain

                # Explain rights in user's language
                response = explain_rights(domain, language)
                session["step"] = "RIGHTS_EXPLAINED"


        # ── STEP 3: RIGHTS EXPLAINED → start collecting details ───
        elif session["step"] == "RIGHTS_EXPLAINED":
            next_question = ask_next_question(
                session["domain"],
                session["collected_details"],
                language
            )
            if next_question == "DETAILS_COMPLETE":
                response = translate_to_user_language(
                    "I have all the details I need. Let me prepare your documents now.",
                    language
                )
            else:
                response = next_question
            session["step"] = "DETAILS_COLLECTION"


        # ── STEP 4: DETAILS COLLECTION ────────────────────────────
        elif session["step"] == "DETAILS_COLLECTION":

            # Save the answer the user just gave
            session["collected_details"] = save_user_answer(
                session["domain"],
                session["collected_details"],
                user_input,
                language
            )

            # Check if more questions are needed
            next_question = ask_next_question(
                session["domain"],
                session["collected_details"],
                language
            )

            if next_question == "DETAILS_COMPLETE":
                # All details collected — generate documents now
                doc_text = fill_all_documents(
                    session["domain"],
                    session["collected_details"]
                )
                session["document_text"] = doc_text

                user_name = session["collected_details"].get("user_name", "User")
                pdf_path = generate_pdf(doc_text, user_name)
                session["pdf_path"] = pdf_path
                session["step"] = "DOCUMENT_GENERATED"

                response = translate_to_user_language(
                    "Your legal documents are ready! "
                    "You can see them in the document box below and download as PDF. "
                    "\n\nPlease reply to receive your step-by-step action guide.",
                    language
                )

            else:
                # More questions to ask
                response = next_question


        # ── STEP 5: DOCUMENT GENERATED → give action guide ────────
        elif session["step"] == "DOCUMENT_GENERATED":
            guide = generate_action_guide(
                session["domain"],
                session["collected_details"],
                language
            )
            session["action_guide"] = guide
            session["step"] = "ACTION_GUIDE_GIVEN"
            response = guide


        # ── STEP 6: ACTION GUIDE GIVEN ────────────────────────────
        elif session["step"] == "ACTION_GUIDE_GIVEN":
            response = translate_to_user_language(
                "Your documents are ready and your full action plan is above. "
                "You can download your PDF document using the button below. "
                "\n\nDo you have any other questions? I am always here to help.",
                language
            )
            session["step"] = "COMPLETED"


        # ── STEP 7: COMPLETED → answer follow-up questions ────────
        elif session["step"] == "COMPLETED":
            response = answer_general_question(user_input, language)


    except Exception:
        print(f"[process_message ERROR]\n{traceback.format_exc()}")
        session["error_count"] = session.get("error_count", 0) + 1
        response = translate_to_user_language(
            "I am sorry, something went wrong. Please try again.",
            language
        )

    # Save conversation history
    if user_input and user_input.strip():
        session["conversation"].append({"role": "user",      "content": user_input})
    session["conversation"].append(    {"role": "assistant", "content": response})

    return (
        response,
        session,
        session.get("pdf_path"),
        session.get("document_text", ""),
    )


# ============================================================

# ============================================================
# SECTION 9 — SESSION HELPERS
# ============================================================

def init_session():
    if "session"  not in st.session_state:
        st.session_state.session  = create_session()
    if "history"  not in st.session_state:
        st.session_state.history  = []
    if "greeted"  not in st.session_state:
        st.session_state.greeted  = False


def send_message(user_input, language):
    response, st.session_state.session, _, _ = process_message(
        user_input, st.session_state.session, language
    )
    st.session_state.history.append(("user",      user_input))
    st.session_state.history.append(("assistant", response))


def progress_bar_html(collected, total):
    pct = int((collected / total) * 100) if total else 0
    return f"""
    <div style="background:var(--color-border-tertiary);border-radius:4px;height:5px;margin-top:6px;">
      <div style="width:{pct}%;height:5px;background:#2e7d32;border-radius:4px;"></div>
    </div>
    <p style="margin:4px 0 0;font-size:11px;color:var(--color-text-secondary);">{collected} of {total} details collected</p>
    """


# ============================================================
# SECTION 10 — STREAMLIT APP
# ============================================================

def main():
    st.set_page_config(
        page_title="NyayMitra — Free AI Legal Assistant",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
    <style>
    /* ── Page ── */
    .block-container { padding-top: 1.5rem !important; max-width: 1100px; }

    /* ── Chat bubbles ── */
    .bubble-bot {
        display: flex; gap: 10px; align-items: flex-start; margin: 8px 0;
    }
    .bubble-user {
        display: flex; gap: 10px; align-items: flex-start;
        flex-direction: row-reverse; margin: 8px 0;
    }
    .avatar {
        width: 32px; height: 32px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 15px; flex-shrink: 0;
        background: var(--color-background-secondary);
        border: 0.5px solid var(--color-border-tertiary);
    }
    .msg-bot {
        background: var(--color-background-secondary);
        border: 0.5px solid var(--color-border-tertiary);
        border-radius: 4px 14px 14px 14px;
        padding: 10px 14px; max-width: 78%;
        font-size: 14px; line-height: 1.65;
        color: var(--color-text-primary);
    }
    .msg-user {
        background: var(--color-background-info);
        border: 0.5px solid var(--color-border-info);
        border-radius: 14px 4px 14px 14px;
        padding: 10px 14px; max-width: 78%;
        font-size: 14px; line-height: 1.65;
        color: var(--color-text-info);
    }

    /* ── Doc ready card ── */
    .doc-card {
        background: var(--color-background-success);
        border: 0.5px solid var(--color-border-success);
        border-radius: 10px; padding: 12px 16px;
        display: flex; align-items: center;
        justify-content: space-between; margin: 8px 0;
    }

    /* ── Stat cards ── */
    .stat-row {
        display: grid; grid-template-columns: repeat(4, 1fr);
        gap: 10px; margin-top: 14px;
    }
    .stat-card {
        background: var(--color-background-secondary);
        border: 0.5px solid var(--color-border-tertiary);
        border-radius: 10px; padding: 12px;
        text-align: center;
    }
    .stat-num {
        font-size: 22px; font-weight: 500;
        color: var(--color-text-primary); margin: 0;
    }
    .stat-label {
        font-size: 11px; color: var(--color-text-secondary);
        margin: 3px 0 0;
    }

    /* ── Domain pill ── */
    .domain-active {
        background: var(--color-background-info);
        border: 0.5px solid var(--color-border-info);
        border-radius: 8px; padding: 6px 10px;
        font-size: 13px; color: var(--color-text-info);
        font-weight: 500;
    }
    .domain-inactive {
        border-radius: 8px; padding: 6px 10px;
        font-size: 13px; color: var(--color-text-secondary);
    }

    /* ── Hide default streamlit header ── */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    init_session()

    # ── SIDEBAR ───────────────────────────────────────────────
    with st.sidebar:

        # Logo
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding-bottom:14px;
                    border-bottom:0.5px solid var(--color-border-tertiary);margin-bottom:14px;">
          <div style="font-size:26px;">⚖️</div>
          <div>
            <p style="margin:0;font-size:16px;font-weight:500;color:var(--color-text-primary);">NyayMitra</p>
            <p style="margin:0;font-size:11px;color:var(--color-text-secondary);">Free AI Legal Assistant</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Language
        st.markdown("<p style='font-size:11px;font-weight:500;color:var(--color-text-secondary);text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px;'>Language</p>", unsafe_allow_html=True)
        language = st.selectbox(
            "Language",
            options=list(SUPPORTED_LANGUAGES.keys()),
            index=0,
            label_visibility="collapsed",
        )
        st.session_state.session["language"] = language

        st.markdown("<div style='margin:14px 0;border-top:0.5px solid var(--color-border-tertiary);'></div>", unsafe_allow_html=True)

        # Active case status
        domain    = st.session_state.session.get("domain")
        details   = st.session_state.session.get("collected_details", {})
        step      = st.session_state.session.get("step", "GREETING")

        if domain:
            required  = REQUIRED_DETAILS.get(domain, [])
            collected = len([f for f in required if f in details])
            total     = len(required)
            st.markdown(f"""
            <div style="background:var(--color-background-success);
                        border:0.5px solid var(--color-border-success);
                        border-radius:10px;padding:12px 14px;margin-bottom:14px;">
              <p style="margin:0;font-size:11px;font-weight:500;
                        color:var(--color-text-success);text-transform:uppercase;
                        letter-spacing:.05em;">Active Case</p>
              <p style="margin:4px 0 0;font-size:14px;font-weight:500;
                        color:var(--color-text-primary);">{domain.capitalize()} — {step.replace('_',' ').title()}</p>
              {progress_bar_html(collected, total)}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:var(--color-background-secondary);
                        border:0.5px solid var(--color-border-tertiary);
                        border-radius:10px;padding:12px 14px;margin-bottom:14px;">
              <p style="margin:0;font-size:13px;color:var(--color-text-secondary);">No active case yet</p>
              <p style="margin:4px 0 0;font-size:12px;color:var(--color-text-secondary);">Describe your problem to begin</p>
            </div>
            """, unsafe_allow_html=True)

        # Legal domains list
        st.markdown("<p style='font-size:11px;font-weight:500;color:var(--color-text-secondary);text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px;'>Legal Domains</p>", unsafe_allow_html=True)

        domains_display = [
            ("👷", "labor",    "Labor & Wages"),
            ("🏠", "tenant",   "Tenant Rights"),
            ("🛒", "consumer", "Consumer Rights"),
            ("👨‍👩‍👧", "family",  "Family & DV"),
            ("📋", "rti",      "RTI"),
            ("🚔", "fir",      "FIR"),
        ]
        for icon, key, label in domains_display:
            css = "domain-active" if domain == key else "domain-inactive"
            st.markdown(f'<div class="{css}">{icon} {label}</div>', unsafe_allow_html=True)

        st.markdown("<div style='margin:14px 0;border-top:0.5px solid var(--color-border-tertiary);'></div>", unsafe_allow_html=True)

        # PDF Download in sidebar
        pdf_path = st.session_state.session.get("pdf_path")
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True,
                )

        # Email
        if pdf_path:
            st.markdown("<p style='font-size:11px;font-weight:500;color:var(--color-text-secondary);text-transform:uppercase;letter-spacing:.05em;margin:10px 0 6px;'>Send to Email</p>", unsafe_allow_html=True)
            email_addr = st.text_input("Email", placeholder="your@email.com", label_visibility="collapsed")
            if st.button("📧 Send Document", use_container_width=True):
                if email_addr and "@" in email_addr:
                    with st.spinner("Sending..."):
                        user_name = details.get("user_name", "User")
                        ok, msg = send_document_by_email(pdf_path, email_addr, user_name, domain or "legal")
                    st.success(msg) if ok else st.error(msg)
                else:
                    st.warning("Enter a valid email address.")

        # Maps
        district = details.get("user_district", "")
        if domain and district:
            maps_url, office = get_maps_link(domain, district)
            st.markdown(f"""
            <div style="margin-top:10px;background:var(--color-background-secondary);
                        border:0.5px solid var(--color-border-tertiary);
                        border-radius:10px;padding:10px 12px;">
              <p style="margin:0;font-size:11px;font-weight:500;
                        color:var(--color-text-secondary);text-transform:uppercase;
                        letter-spacing:.05em;">Nearest Office</p>
              <p style="margin:4px 0 6px;font-size:12px;
                        color:var(--color-text-primary);">{office}</p>
              <a href="{maps_url}" target="_blank"
                 style="font-size:12px;color:var(--color-text-info);">
                 🗺️ Open in Google Maps
              </a>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin:10px 0;'></div>", unsafe_allow_html=True)

        if st.button("🔄 Start New Case", use_container_width=True):
            st.session_state.session = create_session()
            st.session_state.history = []
            st.session_state.greeted = False
            st.rerun()

    # ── MAIN AREA ─────────────────────────────────────────────

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown("""
        <div style="margin-bottom:4px;">
          <span style="font-size:28px;font-weight:500;color:var(--color-text-primary);">⚖️ NyayMitra</span>
          <span style="margin-left:10px;font-size:12px;background:var(--color-background-success);
                       color:var(--color-text-success);padding:3px 10px;
                       border-radius:20px;font-weight:500;">AI Active</span>
        </div>
        <p style="margin:0;font-size:14px;color:var(--color-text-secondary);">
          Free legal help in your language — Know your rights, get your document.
        </p>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin:12px 0;border-top:0.5px solid var(--color-border-tertiary);'></div>", unsafe_allow_html=True)

    # Auto greeting
    if not st.session_state.greeted:
        greeting, st.session_state.session, _, _ = process_message(
            "", st.session_state.session, language
        )
        st.session_state.history.append(("assistant", greeting))
        st.session_state.greeted = True

    # ── CHAT HISTORY ──────────────────────────────────────────
    chat_area = st.container()
    with chat_area:
        doc_text = st.session_state.session.get("document_text")

        for i, (role, msg) in enumerate(st.session_state.history):
            if role == "user":
                st.markdown(f"""
                <div class="bubble-user">
                  <div class="avatar">👤</div>
                  <div class="msg-user">{msg}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bubble-bot">
                  <div class="avatar">⚖️</div>
                  <div class="msg-bot">{msg}</div>
                </div>
                """, unsafe_allow_html=True)

        # Document ready card
        if doc_text and pdf_path:
            st.markdown(f"""
            <div class="doc-card">
              <div>
                <p style="margin:0;font-size:14px;font-weight:500;
                          color:var(--color-text-success);">✅ Documents Ready</p>
                <p style="margin:3px 0 0;font-size:12px;
                          color:var(--color-text-secondary);">
                  Legal documents generated — download PDF from sidebar
                </p>
              </div>
              <p style="margin:0;font-size:22px;">📄</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin:16px 0;border-top:0.5px solid var(--color-border-tertiary);'></div>", unsafe_allow_html=True)

    # ── INPUT AREA ────────────────────────────────────────────
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Type your problem in any language...",
                label_visibility="collapsed",
            )
        with col2:
            submitted = st.form_submit_button("Send →", use_container_width=True)

    if submitted and user_input.strip():
        with st.spinner("NyayMitra is thinking..."):
            send_message(user_input.strip(), language)
        st.rerun()

    # ── VOICE INPUT ───────────────────────────────────────────
    with st.expander("🎤 Speak your problem instead"):
        audio_file = st.audio_input("Click mic to record", label_visibility="collapsed")
        if audio_file is not None:
            with st.spinner("Transcribing voice..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_file.read())
                    tmp_path = tmp.name
                transcribed = voice_to_text(tmp_path)
                os.unlink(tmp_path)
            if transcribed:
                st.success(f"Heard: *{transcribed}*")
                with st.spinner("NyayMitra is thinking..."):
                    send_message(transcribed, language)
                st.rerun()
            else:
                st.error("Could not understand audio. Please type your message instead.")

    # ── DOCUMENT PREVIEW ─────────────────────────────────────
    if doc_text:
        with st.expander("📄 View Full Document"):
            st.text_area(
                "Document",
                value=doc_text,
                height=300,
                label_visibility="collapsed",
            )

    # ── STAT CARDS ───────────────────────────────────────────
    st.markdown("""
    <div class="stat-row">
      <div class="stat-card">
        <p class="stat-num">6</p>
        <p class="stat-label">Legal domains</p>
      </div>
      <div class="stat-card">
        <p class="stat-num">5</p>
        <p class="stat-label">Languages</p>
      </div>
      <div class="stat-card">
        <p class="stat-num">8</p>
        <p class="stat-label">Document types</p>
      </div>
      <div class="stat-card">
        <p class="stat-num">Free</p>
        <p class="stat-label">Always</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── FOOTER ───────────────────────────────────────────────
    st.markdown("""
    <div style="margin-top:20px;padding-top:12px;
                border-top:0.5px solid var(--color-border-tertiary);
                text-align:center;">
      <p style="font-size:11px;color:var(--color-text-secondary);margin:0;">
        ⚠️ NyayMitra provides legal information to help you understand your rights.
        For complex matters, please also consult a qualified lawyer.
        This tool is completely free and does not store your personal information.
      </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()