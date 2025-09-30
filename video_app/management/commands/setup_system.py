"""
Management command to set up the system
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Set up the hand gesture recognition system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a superuser account',
        )
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for superuser',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Email for superuser',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password for superuser',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up hand gesture recognition system...'))
        
        # Create necessary directories
        self.create_directories()
        
        # Create superuser if requested
        if options['create_superuser']:
            self.create_superuser(options)
        
        # Set up initial data
        self.setup_initial_data()
        
        self.stdout.write(self.style.SUCCESS('System setup completed successfully!'))

    def create_directories(self):
        """Create necessary directories"""
        directories = [
            'logs',
            'media/gesture_videos',
            'media/processed_videos',
            'media/text_to_sign',
            'media/voice_to_sign',
            'media/voice_files',
            'media/temp',
        ]
        
        for directory in directories:
            full_path = os.path.join(settings.BASE_DIR, directory)
            os.makedirs(full_path, exist_ok=True)
            self.stdout.write(f'Created directory: {directory}')

    def create_superuser(self, options):
        """Create superuser account"""
        username = options['username']
        email = options['email']
        password = options['password']
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))
            return
        
        User.objects.create_superuser(username, email, password)
        self.stdout.write(self.style.SUCCESS(f'Created superuser: {username}'))

    def setup_initial_data(self):
        """Set up initial data"""
        # This could include creating default gesture types, 
        # sample sessions, or other initial data
        self.stdout.write('Initial data setup completed')
