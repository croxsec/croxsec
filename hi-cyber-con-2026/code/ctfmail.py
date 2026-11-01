import imaplib, json, re
creds = json.load(open('/root/.openclaw/workspace/business/hosting/creds.json'))
host = (creds.get('mail_server',{}).get('imap') or 'mail.croxsec.com').split(':')[0]
M = imaplib.IMAP4_SSL(host, 993)
M.login('crox@croxsec.com', creds['mailboxes']['crox@croxsec.com'])
M.select('INBOX')
typ, data = M.search(None, 'ALL')
ids = data[0].split()
print("total:", len(ids))
found = []
for mid in ids[-25:]:
    typ, d = M.fetch(mid, '(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])')
    hdr = d[0][1].decode(errors='replace')
    if re.search(r'pink|bayern|chronos|csctf|confirm|ctfd|ctf', hdr, re.I):
        found.append(hdr.strip()[:300])
for f in found:
    print('---\n', f)
if not found:
    print("(sin correos de CTFs en los ultimos 25)")
M.logout()
