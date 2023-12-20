#import yagmail



### make instance variables for log.email and log.app_pass
### set instance variables from config on init
### if config[email] or config[pass] == NONE prompt through telegram

#yag = yagmail.SMTP(user="8xima8", password="dcdjdbwgpabakyoq")

class Log:
    
    #def __init__(self):
        #self.message_queue = []

    @staticmethod 
    def info(message: str):
        print(f'INFO: {message}', flush=True)

    @staticmethod
    def error(message: str):
        print(f'ERROR: {message}', flush=True)
        

   # @staticmethod
   # def block_alert(message: str, accepted: bool) -> str:
   #     """sends out a message for an accepted or missed block"""
   #     match = re.search(r"Location: (.*)\-", message)
   #     if match:
   #         station = match.group(1)
   #     else:
    #        station = None

        #if accepted:
        #    body = f"---> Block Accepted from {station} <---\n"
        #else: 
        #    body = f"Missed block from {station}\n"
        #body += message
        #return body 
