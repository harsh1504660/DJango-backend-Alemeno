from django.core.management.base import BaseCommand
from loans.tasks import ingest_initial_data_task

class Command(BaseCommand):
    help = 'Trigger ingestion of provided excel files'
    def handle(self, *args, **kwargs):
        res = ingest_initial_data_task()
        self.stdout.write(str(res))
