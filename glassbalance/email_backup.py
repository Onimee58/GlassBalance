"""User-initiated encrypted backup transfer through an email account.

This is intentionally NOT conflict-aware bidirectional sync. It saves encrypted
SQLite snapshots as email attachments; restoring one replaces the local ledger
only after explicit user confirmation and a local safety backup.
"""
from __future__ import annotations

import imaplib
import os
import smtplib
import ssl
from datetime import datetime, timezone
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

MAGIC=b"GBAL-ENC-V1\0"
SUBJECT="GlassBalance encrypted backup"


def _key(secret: str, salt: bytes) -> bytes:
    if len(secret)<12:
        raise ValueError("Encryption passphrase must contain at least 12 characters.")
    kdf=Scrypt(salt=salt,length=32,n=2**15,r=8,p=1)
    return kdf.derive(secret.encode("utf-8"))


def encrypt_snapshot(payload: bytes, passphrase: str) -> bytes:
    if not payload.startswith(b"SQLite format 3\x00"):
        raise ValueError("Expected a valid SQLite backup for encryption.")
    salt=os.urandom(16)
    nonce=os.urandom(12)
    cipher=AESGCM(_key(passphrase,salt)).encrypt(nonce,payload,MAGIC)
    return MAGIC+salt+nonce+cipher


def decrypt_snapshot(payload: bytes, passphrase: str) -> bytes:
    if not payload.startswith(MAGIC) or len(payload)<len(MAGIC)+16+12+16:
        raise ValueError("This attachment is not a GlassBalance encrypted backup.")
    offset=len(MAGIC)
    salt=payload[offset:offset+16]
    nonce=payload[offset+16:offset+28]
    cipher=payload[offset+28:]
    try:
        data=AESGCM(_key(passphrase,salt)).decrypt(nonce,cipher,MAGIC)
    except Exception as exc:
        raise ValueError("Unable to decrypt backup. Check your passphrase or attachment.") from exc
    if not data.startswith(b"SQLite format 3\x00"):
        raise ValueError("Decrypted contents are not a SQLite backup.")
    return data


def send_backup(email: str, app_password: str, smtp_host: str, passphrase: str,
                sqlite_data: bytes, smtp_port: int=465) -> str:
    email=email.strip()
    if "@" not in email or not smtp_host.strip() or not app_password:
        raise ValueError("Provide an email address, SMTP server, and email app password.")
    encrypted=encrypt_snapshot(sqlite_data,passphrase)
    timestamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename=f"glassbalance-{timestamp}.gbenc"
    msg=EmailMessage()
    msg["From"]=email
    msg["To"]=email
    msg["Subject"]=SUBJECT
    msg.set_content("An encrypted GlassBalance database backup is attached. The encryption passphrase is not included.")
    msg.add_attachment(encrypted,maintype="application",subtype="octet-stream",filename=filename)
    context=ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_host.strip(),int(smtp_port),timeout=30,context=context) as smtp:
        smtp.login(email,app_password)
        smtp.send_message(msg)
    return filename


def download_latest_backup(email: str, app_password: str, imap_host: str,
                           imap_port: int=993) -> bytes:
    email=email.strip()
    if "@" not in email or not imap_host.strip() or not app_password:
        raise ValueError("Provide an email address, IMAP server, and email app password.")
    client=imaplib.IMAP4_SSL(imap_host.strip(),int(imap_port),ssl_context=ssl.create_default_context(),timeout=30)
    try:
        client.login(email,app_password)
        ok,_=client.select("INBOX",readonly=True)
        if ok!="OK":
            raise RuntimeError("Cannot open this email inbox.")
        ok,ids=client.search(None,"SUBJECT",'"GlassBalance encrypted backup"')
        if ok!="OK" or not ids or not ids[0]:
            raise FileNotFoundError("No GlassBalance backup messages were found in the inbox.")
        # Search newest messages first. The latest message that actually contains
        # our encrypted attachment is used. Authenticity is AES-GCM verified.
        for number in reversed(ids[0].split()[-100:]):
            status,response=client.fetch(number,"(RFC822)")
            if status!="OK":
                continue
            for part in response:
                if not isinstance(part,tuple) or not isinstance(part[1],bytes):
                    continue
                msg=BytesParser(policy=policy.default).parsebytes(part[1])
                for attachment in msg.iter_attachments():
                    filename=attachment.get_filename() or ""
                    if filename.endswith(".gbenc"):
                        payload=attachment.get_payload(decode=True)
                        if payload and payload.startswith(MAGIC):
                            return payload
        raise FileNotFoundError("No usable GlassBalance encrypted attachment was found.")
    finally:
        try:
            client.logout()
        except Exception:
            pass
