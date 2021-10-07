from django.core.mail import send_mail

from infoblox.helpers.Log import Log


class Mail:
    @staticmethod
    def send(user: dict, subject: str, message: str) -> None:
        try:
            Log.actionLog("Sending email", user)

            send_mail(
                subject,
                message,
                'default-from@automation.local',
                ['default-to@automation.local'],
                fail_silently=False,
            )
        except Exception as e:
            Log.log("Sending email failed: "+str(e.__str__()))
