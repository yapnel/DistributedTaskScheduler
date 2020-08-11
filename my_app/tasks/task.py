import celery
import subprocess
import os
from celery.exceptions import Ignore

@celery.task()
def sayHello(data1):
    print(data1)     

@celery.task(bind=True)
def unpivot(self, filename, sheet, database, mode, tablename):
    process = subprocess.Popen(['python','-u', os.path.join(os.path.dirname(os.path.realpath(__file__)),'unpivot','unpivot.py') ,'--file='+filename,'--sheet='+sheet, '--database='+database, '--mode='+mode, '--tablename='+tablename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        self.update_state(state='FAILURE', meta={'exc': stderr.decode('utf-8')})        
        raise Exception(stderr.decode('utf-8') + ' for Task ID = ' + self.request.id)    
    else:
        self.update_state(state='SUCCESS', meta={'exc': stdout.decode('utf-8')})       
        return stdout.decode('utf-8')
