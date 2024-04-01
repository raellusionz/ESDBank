from mailersend import emails
from dotenv import dotenv_values

mailer = emails.NewEmail(dotenv_values('../.env.development.local')['EMAIL_API'])

def sendEmail(name1, name2, email, transactionAmount, transactionDate, transactionID, content):

    # define an empty dict to populate with mail values
    mail_body = {}

    mail_from = {
        "name": "ESDBank",
        "email": "esdbank@trial-3z0vklo89ee47qrx.mlsender.net",
    }

    recipients = [
        {
            "name": name1,
            "email": email,
        }
    ]

    reply_to = {
        "name": "Name",
        "email": "reply@domain.com",
    }

    content =f"""<h1>Transaction completed!</h1>
                <p>Dear {name1},<br>
                We're thrilled to inform you that a transaction has been successfully completed with your bank account. Your financial affairs are now up to date!</p>
                <p><b>Transaction Details<b><br>
                    Transaction ID: {transactionID}<br>
                    Date: {transactionDate[:10]}<br>
                    Time: {transactionDate[11:]}<br>
                    Amount: ${transactionAmount}<br>
                    Description: {content} {name2}</p>
                <p>Thank you for trusting ESDBank for your banking needs. We appreciate your continued business.</p>"""

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Hello!", mail_body)
    mailer.set_html_content(content, mail_body)
    mailer.set_plaintext_content("This is the text content", mail_body)
    mailer.set_reply_to(reply_to, mail_body)

    # using print() will also return status code and data
    mailer.send(mail_body)

def sendEmail2(inviter, invitee, email, group_name):

    # define an empty dict to populate with mail values
    mail_body = {}

    mail_from = {
        "name": "ESDBank",
        "email": "esdbank@trial-3z0vklo89ee47qrx.mlsender.net",
    }

    recipients = [
        {
            "name": invitee,
            "email": email,
        }
    ]

    reply_to = {
        "name": "Name",
        "email": "reply@domain.com",
    }

    content =f"""<h1>You have been added to a group!</h1>
                <p>Dear {invitee},<br>
                You have been added to the Splitpay group "{group_name}" created by {inviter}</p>
                <p>Thank you for trusting ESDBank for your payment needs. We appreciate your continued business.</p>"""

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Hello!", mail_body)
    mailer.set_html_content(content, mail_body)
    mailer.set_plaintext_content("This is the text content", mail_body)
    mailer.set_reply_to(reply_to, mail_body)

    # using print() will also return status code and data
    mailer.send(mail_body)