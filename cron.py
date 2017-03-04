from django.core import management
from django_cron import CronJobBase, Schedule

class BackupsJob(CronJobBase):
    '''Back-up the database every day, after all other jobs have run.'''

    RUN_AT_TIMES = ['01:00']
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'meta.cron.BackupsJob'

    def do(self):
        management.call_command('dbbackup', '--quiet', '--compress', '--clean')
        management.call_command('mediabackup', '--quiet', '--compress', '--clean')

