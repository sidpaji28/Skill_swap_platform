import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import uuid
from schema_definitions import UserProfile

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase not available, using mock database")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        if SUPABASE_AVAILABLE:
            self.url = os.getenv('SUPABASE_URL', 'your-supabase-url')
            self.key = os.getenv('SUPABASE_KEY', 'your-supabase-key')
            if self.url == 'your-supabase-url' or self.key == 'your-supabase-key':
                logger.warning("Supabase credentials not configured. Using mock DB.")
                self.client = None
                self.use_mock = True
            else:
                try:
                    self.client: Client = create_client(self.url, self.key)
                    self.use_mock = False
                    logger.info("Connected to Supabase.")
                except Exception as e:
                    logger.error(f"Failed to connect to Supabase: {e}")
                    self.client = None
                    self.use_mock = True
        else:
            self.client = None
            self.use_mock = True

        if self.use_mock:
            self._init_mock_data()

    def _init_mock_data(self):
        self.mock_users = {}

        sample_users = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Alice Johnson',
                'email': 'alice@example.com',
                'password_hash': self._hash_password("alice123"),
                'location': 'Delhi',
                'skills_offered': ['Python', 'Data Science'],
                'skills_wanted': ['React'],
                'availability': 'Evenings',
                'is_public': True,
                'created_at': datetime.now().isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Bob Verma',
                'email': 'bob@example.com',
                'password_hash': self._hash_password("bob123"),
                'location': 'Mumbai',
                'skills_offered': ['React', 'JavaScript'],
                'skills_wanted': ['Python'],
                'availability': 'Weekends',
                'is_public': True,
                'created_at': datetime.now().isoformat()
            }
        ]

        for user in sample_users:
            self.mock_users[user['id']] = user

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, hashed: str) -> bool:
        return self._hash_password(password) == hashed

    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        if self.use_mock:
            for user in self.mock_users.values():
                if user['email'] == email and self._verify_password(password, user['password_hash']):
                    return user
            return None

        try:
            response = self.client.table('users').select('*').eq('email', email).execute()
            if response.data:
                user = response.data[0]
                if self._verify_password(password, user['password_hash']):
                    del user['password_hash']
                    return user
        except Exception as e:
            logger.error(f"Auth error: {e}")
        return None

    def _add_user_skills(self, user_id: str, skills: List[str], skill_type: str):
        if self.use_mock:
            return
        try:
            for skill in skills:
                self.client.table('user_skills').insert({
                    'user_id': user_id,
                    'skill': skill,
                    'type': skill_type
                }).execute()
        except Exception as e:
            logger.error(f"Failed to insert skills for {user_id}: {e}")

    def create_user(self, user_profile: UserProfile, password: str) -> Optional[str]:
        """
        Insert a new user and their skills
        """
        if self.use_mock:
            user_id = str(uuid.uuid4())
            user_data = {
                'id': user_id,
                'name': user_profile.name,
                'email': user_profile.email,
                'password_hash': self._hash_password(password),
                'location': user_profile.location,
                'availability': user_profile.availability,
                'is_public': user_profile.is_public,
                'created_at': datetime.now().isoformat(),
                'skills_offered': user_profile.skills_offered,
                'skills_wanted': user_profile.skills_wanted,
                'rating': 0.0,
                'completed_swaps': 0
            }
            self.mock_users[user_id] = user_data
            return user_id

        try:
            user_data = {
                'name': user_profile.name,
                'email': user_profile.email,
                'location': user_profile.location,
                'availability': user_profile.availability,
                'is_public': user_profile.is_public,
                'password_hash': self._hash_password(password)
            }

            response = self.client.table('users').insert(user_data).execute()

            if response.data:
                user_id = response.data[0]['id']
                self._add_user_skills(user_id, user_profile.skills_offered, 'offered')
                self._add_user_skills(user_id, user_profile.skills_wanted, 'wanted')
                return user_id

        except Exception as e:
            logger.error(f"Error inserting user: {e}")
        return None

    def get_all_users(self, exclude_id: Optional[str] = None) -> List[Dict]:
        if self.use_mock:
            users = list(self.mock_users.values())
            if exclude_id:
                users = [u for u in users if u["id"] != exclude_id]
            return users

        try:
            users_response = self.client.table('users').select('*').execute()
            users = users_response.data if users_response.data else []

            skills_response = self.client.table('user_skills').select('*').execute()
            skills_data = skills_response.data if skills_response.data else []

            user_skills = {}
            for s in skills_data:
                uid = s['user_id']
                if uid not in user_skills:
                    user_skills[uid] = {'skills_offered': [], 'skills_wanted': []}
                skill_type = 'skills_offered' if s['type'] == 'offered' else 'skills_wanted'
                user_skills[uid][skill_type].append(s['skill'])

            for u in users:
                u_id = u['id']
                u['skills_offered'] = user_skills.get(u_id, {}).get('skills_offered', [])
                u['skills_wanted'] = user_skills.get(u_id, {}).get('skills_wanted', [])

            if exclude_id:
                users = [u for u in users if u["id"] != exclude_id]

            return users

        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []
