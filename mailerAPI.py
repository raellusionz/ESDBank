from mailersend import emails
from dotenv import dotenv_values

mailer = emails.NewEmail(dotenv_values('.env.development.local')['MAILER_EMAIL_API'])

# define an empty dict to populate with mail values
mail_body = {}

mail_from = {
    "name": "ESDBank",
    "email": "esdbank@trial-3z0vklo89ee47qrx.mlsender.net",
}

recipients = [
    {
        "name": "Sarah Thauheed",
        "email": "sthauheed.2022@scis.smu.edu.sg",
    }
]

reply_to = {
    "name": "Name",
    "email": "reply@domain.com",
}

mailer.set_mail_from(mail_from, mail_body)
mailer.set_mail_to(recipients, mail_body)
mailer.set_subject("Hello!", mail_body)
mailer.set_html_content("This is the HTML content", mail_body)
mailer.set_plaintext_content("This is the text content", mail_body)
mailer.set_reply_to(reply_to, mail_body)

# using print() will also return status code and data
mailer.send(mail_body)