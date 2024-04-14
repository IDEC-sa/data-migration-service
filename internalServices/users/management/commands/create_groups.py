from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _create_tags(self):
        view_quote = Permission.objects.get(codename='view_quoterequest')
        add_quote = Permission.objects.get(codename='add_quoterequest')
        change_quote = Permission.objects.get(codename='change_quoterequest')
        delete_quote = Permission.objects.get(codename='delete_quoterequest')
        validate_quote = Permission.objects.get(codename='can_validate_quote')
        add_static_data = Permission.objects.get(codename='can_add_static_to_quote')
        draften_quote = Permission.objects.get(codename='can_draften_quote')
        approve_quote = Permission.objects.get(codename='can_approve_quote')
        disapprove_quote = Permission.objects.get(codename='can_disapprove_quote')
        review_quote = Permission.objects.get(codename='can_review_quote')
        dir_permissions = [
            view_quote,
            approve_quote,
            disapprove_quote
        ]
        sman_permissions = [
            view_quote,
            add_quote,
            change_quote,
            delete_quote,
            validate_quote,
            add_static_data,
            draften_quote,
            review_quote
        ]

        salesmen = Group.objects.get_or_create(name='salesmen')[0]

        dirs = Group.objects.get_or_create(name='salesdirectors')[0]
        dirs.save()
        salesmen.save()
        dirs.permissions.set(dir_permissions)
        salesmen.permissions.set(sman_permissions)


    def handle(self, *args, **options):
        self._create_tags()