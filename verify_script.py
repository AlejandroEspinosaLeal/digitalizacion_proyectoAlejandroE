import urllib.request
import imaplib
import email
import re

print("[*] 1. Connecting to Gmail IMAP...")
try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('espinosaale66@gmail.com', 'oyqfcqddnprqyxrx')
    mail.select('inbox')
    
    status, data = mail.search(None, 'ALL')
    mail_ids = data[0].split()
    
    link_found = False
    
    print("[*] Checking last 15 emails for Supabase verification links...")
    # search the last 15 emails
    for i in reversed(mail_ids[-15:]):
        status, msg_data = mail.fetch(i, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/html" or part.get_content_type() == "text/plain":
                            body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                else:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                
                # Look for confirmation link
                if "dnbsgjmscuycjwrnknyj.supabase.co" in body and ("verify" in body or "confirm" in body.lower()):
                    links = re.findall(r'href=[\'"]?(https?://[^\'" >]+)', body)
                    for l in links:
                        if "verify" in l or "auth" in l:
                            print(f"[+] Found verification link: {l}")
                            req_ver = urllib.request.Request(l, method='GET')
                            try:
                                urllib.request.urlopen(req_ver)
                                print("[+] Account verified successfully via link!")
                            except urllib.error.HTTPError as he:
                                print(f"[~] Verification request returned: {he.code} (usually OK/redirect)")
                            link_found = True
                            break
        if link_found:
            break
            
    if not link_found:
        print("[-] Could not find any email verification link in the recent inbox.")
except Exception as ex:
    print("[-] Exception in IMAP:", str(ex))
