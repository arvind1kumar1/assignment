import smtplib
from email.message import EmailMessage
 
import smtplib
 
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pytz
import os

serverEmail = "sachin65681@gmail.com"
password = "abc987!@#"

def sendMailOnTransaction(amount,debiterUser,receiverUser,debiter,receiver):
    msg = MIMEMultipart()
    msg['From'] = serverEmail
    msg['Subject'] = 'Transaction details'   
    msg['To'] = debiter
    data = "your account debited successfull "+str(amount)
    body = data
    msg.attach(MIMEText(body, 'plain'))
    # server.send_message(msg, from_addr=serverEmail, to_addrs=None)

    msg1 = MIMEMultipart()
    msg1['From'] = serverEmail
    msg1['Subject'] = 'Transaction details'   
    msg1['To'] = receiver
    data = "your account credited successfull "+str(amount)
    body = data
    msg1.attach(MIMEText(body, 'plain'))
    # msg['To'] = debiter
    # msg['Subject'] = 'simple email in python'
    # message = 'here is the email'
    # msg.attach(MIMEText(body))
    
    mailserver = smtplib.SMTP('smtp.gmail.com',587)
    # identify ourselves to smtp gmail client
    mailserver.ehlo()
    # secure our email with tls encryption
    mailserver.starttls()
    # re-identify ourselves as an encrypted connection
    mailserver.ehlo()
    mailserver.login(serverEmail, password)
    
    mailserver.sendmail(serverEmail,msg["To"],msg.as_string())
    mailserver.sendmail(serverEmail,msg1["To"],msg1.as_string())    
    mailserver.quit()

# def sendExcelToManager(fileName,managerEmail):    
#     import ipdb
#     ipdb.set_trace()

#     local_path = os.path.abspath(os.path.curdir)
#     filepath = ""
#     subject = ""
#     sender_email = ""
#     receiver_email = ""
#     password = ""
#     filepath = local_path + "\\sendExcel\\" + fileName
#     subject = "Transaction Email"   

#     sender_email = serverEmail
#     receiver_email = managerEmail
#     # receiver_email = "chatbot@bidco-oil.com"
#     password = password

#     # Create a multipart message and set headers
#     message = MIMEMultipart()
#     message["From"] = sender_email
#     message["To"] = receiver_email
#     message["Subject"] = subject
#     message["Bcc"] = receiver_email  # Recommended for mass emails

#     # Add body to email
#     body = "PFA"
#     message.attach(MIMEText(body, "plain"))

#     filename = fileName
#     # Open PDF file in binary mode
#     with open(filepath, "rb") as attachment:        
#         part = MIMEBase("application", "octet-stream")
#         part.set_payload(attachment.read())
#     # Encode file in ASCII characters to send by email
#     encoders.encode_base64(part)
#     # Add header as key/value pair to attachment part
#     part.add_header(
#         "Content-Disposition",
#         f"attachment; filename= {filename}",
#     )
#     # Add attachment to message and convert message to string
#     message.attach(part)
#     text = message.as_string()

#     # mailserver = smtplib.SMTP('outlook.office365.com', 587)
#     mailserver = smtplib.SMTP('smtp.gmail.com',587)
#     mailserver.ehlo()
#     mailserver.starttls()
#     mailserver.login(sender_email, password)
#     mailserver.sendmail(sender_email, receiver_email, text)
#     mailserver.quit()

if __name__ == "__main__":
    sendExcelToManager()
    