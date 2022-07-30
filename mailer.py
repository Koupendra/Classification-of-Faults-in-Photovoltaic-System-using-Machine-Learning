import yagmail

def sendMail(receiver, fault, ardId):
    senderEmail = None     # Email Id of the Sender
    appPassword = None     # Google account app password
    yag = yagmail.SMTP(senderEmail, appPassword)
    contents = ['Hi owner!', f'There is a possible {fault} in PV array attached to Microcontroller-{ardId}!', 
                'Please take necessary actions soon',
                "Once rectified, please press and hold the 'RESET' Button for 2 seconds"]
    yag.send(f'{receiver}', 'Important! Fault Alert!', contents)
