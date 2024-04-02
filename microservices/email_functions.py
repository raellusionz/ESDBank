from mailersend import emails
from dotenv import dotenv_values

mailer = emails.NewEmail(dotenv_values('../.env.development.local')['EMAIL_API'])


def sendTransferFundsNotif(name1, name2, email, transactionAmount, transactionDate, transactionID, content):

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

    content =f"""<p>Hi {name1},</p>
                <p>We're thrilled to inform you that a transaction has been successfully completed with your bank account. Your financial affairs are now up to date!</p>
                <p><b><u>Transaction Details</u></b><br>
                    <b>Transaction ID:</b> {transactionID}<br>
                    <b>Date:</b> {transactionDate[:10]}<br>
                    <b>Time:</b> {transactionDate[11:]}<br>
                    <b>Amount:</b> ${transactionAmount}<br>
                    <b>Description:</b> {content} {name2}</p>
                <p>Thank you for trusting ESDBank for your banking needs. We appreciate your continued business.</p>
                <p>Best,<br>
                    <b>ESDBank Team</b></p>"""


    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("[ESDBank] Notice of Successful Transaction", mail_body)
    mailer.set_html_content(content, mail_body)
    mailer.set_plaintext_content("This is the text content", mail_body)
    mailer.set_reply_to(reply_to, mail_body)


    # using print() will also return status code and data
    mailer.send(mail_body)

    # using print() will also return status code and data
    mailer.send(mail_body)

def sendCreateGroupNotif(inviter, invitee, email, group_name):

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


    content =f"""<p>Hi {invitee},</p>
                <p>Exciting news! You've been added to a new SplitPay group in ESDBank.</p>
                <p><b><u>Group Details</u></b><br>
                <b>Group name:</b> {group_name}<br>
                <b>Created by:</b> {inviter}<br>
                <p>This group is designed to simplify expense splitting. View shared expenses, initiate split requests, and stay updated with real-time notifications.</p>
                <p>Thank you for trusting ESDBank for your banking needs. We appreciate your continued business.</p>
                <p>Best,<br>
                    <b>ESDBank Team</b></p>"""


    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("[ESDBank] Welcome to your new SplitPay group!", mail_body)
    mailer.set_html_content(content, mail_body)
    mailer.set_plaintext_content("This is the text content", mail_body)
    mailer.set_reply_to(reply_to, mail_body)


    # using print() will also return status code and data
    mailer.send(mail_body)

# requesterName
# payerName
# payerEmail
# requestAmount
# groupName
# requestDateTime

def sendSplitRequestNotif(requesterName, payerName, payerEmail, requestAmount, groupName, requestDateTime):

    # define an empty dict to populate with mail values
    mail_body = {}

    mail_from = {
        "name": "ESDBank",
        "email": "esdbank@trial-3z0vklo89ee47qrx.mlsender.net",
    }

    recipients = [
        {
            "name": payerName,
            "email": payerEmail,
        }
    ]

    reply_to = {
        "name": "Name",
        "email": "reply@domain.com",
    }


    content =f"""<p>Hi {payerName},</p>
                <p>You've received a new SplitPay request from {requesterName}!</p>
                <p><b><u>Request Details</u></b><br>
                    <b>Group Name:</b> {groupName}
                    <b>Date:</b> {requestDateTime[:10]}<br>
                    <b>Time:</b> {requestDateTime[11:]}<br>
                    <b>Amount:</b> ${requestAmount}<br>
                <p>To review this request, please log in to your ESDBank account and navigate to the group section.</p>
                <p>Thank you for trusting ESDBank for your banking needs. We appreciate your continued business.</p>
                <p>Best,<br>
                    <b>ESDBank Team</b></p>"""


    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("[ESDBank] New SplitPay Request", mail_body)
    mailer.set_html_content(content, mail_body)
    mailer.set_plaintext_content("This is the text content", mail_body)
    mailer.set_reply_to(reply_to, mail_body)


    # using print() will also return status code and data
    mailer.send(mail_body)
