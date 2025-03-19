import imaplib

# Example usage of imaplib
mail = imaplib.IMAP4_SSL('imap.gmail.com')  # Using Gmail's IMAP server
mail.login('your_email@gmail.com', 'your_password')
mail.select('inbox')

# Search all emails
status, messages = mail.search(None, "ALL")
email_ids = messages[0].split()

for email_id in email_ids:
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    print(msg_data)

mail.logout()
