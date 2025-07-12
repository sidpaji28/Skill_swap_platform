"""
AI-powered skill matching using sentence transformers for semantic similarity
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer, util
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillMatcher:
    """
    AI-powered skill matching using sentence transformers
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the skill matcher with a sentence transformer model
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded sentence transformer model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            # Fallback to a basic model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def encode_skills(self, skills: List[str]) -> np.ndarray:
        """
        Encode skills into embeddings
        
        Args:
            skills: List of skill descriptions
            
        Returns:
            numpy array of embeddings
        """
        if not skills:
            return np.array([])
        
        # Clean and normalize skills
        cleaned_skills = [self._clean_skill(skill) for skill in skills]
        
        try:
            embeddings = self.model.encode(cleaned_skills, convert_to_tensor=True)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to encode skills: {e}")
            return np.array([])
    
    def _clean_skill(self, skill: str) -> str:
        """
        Clean and normalize skill text
        
        Args:
            skill: Raw skill description
            
        Returns:
            Cleaned skill description
        """
        # Remove extra whitespace and convert to lowercase
        skill = skill.strip().lower()
        
        # Expand common abbreviations
        skill_expansions = {
            'js': 'javascript',
            'py': 'python',
            'html/css': 'html css web design',
            'ui/ux': 'user interface user experience design',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'db': 'database',
            'sql': 'structured query language database',
            'api': 'application programming interface',
            'git': 'version control git',
            'docker': 'containerization docker',
            'aws': 'amazon web services cloud computing',
            'gcp': 'google cloud platform',
            'azure': 'microsoft azure cloud',
        }
        
        for abbr, expansion in skill_expansions.items():
            if abbr in skill:
                skill = skill.replace(abbr, expansion)
        
        return skill
    
    def get_similarity(self, skills1: List[str], skills2: List[str]) -> float:
        """
        Calculate similarity between two skill sets
        
        Args:
            skills1: First set of skills
            skills2: Second set of skills
            
        Returns:
            Similarity score between 0 and 1
        """
        if not skills1 or not skills2:
            return 0.0
        
        try:
            embeddings1 = self.encode_skills(skills1)
            embeddings2 = self.encode_skills(skills2)
            
            if embeddings1.size == 0 or embeddings2.size == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity_matrix = util.cos_sim(embeddings1, embeddings2)
            
            # Return the maximum similarity (best match)
            max_similarity = similarity_matrix.max().item()
            return max_similarity
        
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def find_skill_matches(self, target_skill: str, available_skills: List[str], 
                          threshold: float = 0.3) -> List[Tuple[str, float]]:
        """
        Find matching skills for a target skill
        
        Args:
            target_skill: The skill to find matches for
            available_skills: List of available skills to match against
            threshold: Minimum similarity threshold
            
        Returns:
            List of (skill, similarity_score) tuples, sorted by similarity
        """
        if not available_skills:
            return []
        
        try:
            target_embedding = self.encode_skills([target_skill])
            available_embeddings = self.encode_skills(available_skills)
            
            if target_embedding.size == 0 or available_embeddings.size == 0:
                return []
            
            # Calculate similarities
            similarities = util.cos_sim(target_embedding, available_embeddings)[0]
            
            # Create list of matches above threshold
            matches = []
            for i, similarity in enumerate(similarities):
                score = similarity.item()
                if score >= threshold:
                    matches.append((available_skills[i], score))
            
            # Sort by similarity score (descending)
            matches.sort(key=lambda x: x[1], reverse=True)
            
            return matches
        
        except Exception as e:
            logger.error(f"Failed to find skill matches: {e}")
            return []

# Global matcher instance
_matcher = None

def get_matcher() -> SkillMatcher:
    """
    Get the global skill matcher instance
    
    Returns:
        SkillMatcher instance
    """
    global _matcher
    if _matcher is None:
        _matcher = SkillMatcher()
    return _matcher

def match_users(user_wanted_skills: List[str], all_users: List[Dict], 
                top_k: int = 5) -> List[Tuple[Dict, float]]:
    """
    Find the best user matches based on wanted skills
    
    Args:
        user_wanted_skills: Skills the current user wants to learn
        all_users: List of all available users
        top_k: Number of top matches to return
        
    Returns:
        List of (user_dict, match_score) tuples
    """
    if not user_wanted_skills or not all_users:
        return []
    
    matcher = get_matcher()
    matches = []
    
    for user in all_users:
        if not user.get('skills_offered'):
            continue
        
        # Calculate match score
        match_score = matcher.get_similarity(user_wanted_skills, user['skills_offered'])
        
        # Add contextual scoring
        contextual_score = _calculate_contextual_score(user, user_wanted_skills)
        
        # Combine scores (70% similarity, 30% contextual)
        final_score = (match_score * 0.7) + (contextual_score * 0.3)
        
        matches.append((user, final_score))
    
    # Sort by match score and return top k
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:top_k]

def _calculate_contextual_score(user: Dict, wanted_skills: List[str]) -> float:
    """
    Calculate contextual score based on user profile
    
    Args:
        user: User profile dictionary
        wanted_skills: Skills the current user wants to learn
        
    Returns:
        Contextual score between 0 and 1
    """
    score = 0.0
    factors = 0
    
    # Availability match (if user has specific availability preferences)
    if user.get('availability'):
        score += 0.2
        factors += 1
    
    # Location proximity (if location is provided)
    if user.get('location'):
        score += 0.1
        factors += 1
    
    # Profile completeness
    profile_fields = ['name', 'skills_offered', 'skills_wanted', 'availability']
    filled_fields = sum(1 for field in profile_fields if user.get(field))
    completeness = filled_fields / len(profile_fields)
    score += completeness * 0.3
    factors += 1
    
    # Skill diversity (users with more skills might be better teachers)
    if user.get('skills_offered'):
        skill_count = len(user['skills_offered'])
        diversity_score = min(skill_count / 10, 1.0)  # Cap at 10 skills
        score += diversity_score * 0.2
        factors += 1
    
    # Mutual interest (if user wants to learn what current user offers)
    if user.get('skills_wanted'):
        # This would need current user's offered skills as input
        # For now, just give a small bonus for having wanted skills
        score += 0.1
        factors += 1
    
    return score / factors if factors > 0 else 0.0

def get_skill_similarity(skill1: str, skill2: str) -> float:
    """
    Get similarity between two individual skills
    
    Args:
        skill1: First skill
        skill2: Second skill
        
    Returns:
        Similarity score between 0 and 1
    """
    matcher = get_matcher()
    return matcher.get_similarity([skill1], [skill2])

def find_complementary_skills(user_skills: List[str], wanted_skills: List[str]) -> List[str]:
    """
    Find skills that complement the user's existing skills
    
    Args:
        user_skills: Current user's skills
        wanted_skills: Skills the user wants to learn
        
    Returns:
        List of complementary skill suggestions
    """
    # Skill complement mapping
    skill_complements = {
        'python': ['data science', 'machine learning', 'web development', 'automation'],
        'javascript': ['react', 'node.js', 'vue.js', 'typescript', 'web design'],
        'html': ['css', 'javascript', 'web design', 'ui/ux'],
        'css': ['html', 'javascript', 'web design', 'sass'],
        'photoshop': ['illustrator', 'graphic design', 'ui/ux', 'photography'],
        'excel': ['data analysis', 'vba', 'power bi', 'sql'],
        'marketing': ['content writing', 'seo', 'social media', 'analytics'],
        'guitar': ['music theory', 'piano', 'songwriting', 'recording'],
        'cooking': ['baking', 'nutrition', 'food photography', 'recipe writing'],
        'writing': ['editing', 'content marketing', 'copywriting', 'blogging'],
        'photography': ['photoshop', 'lightroom', 'video editing', 'composition'],
        'drawing': ['painting', 'digital art', 'illustration', 'graphic design'],
        'yoga': ['meditation', 'fitness', 'nutrition', 'mindfulness'],
        'spanish': ['portuguese', 'french', 'translation', 'teaching'],
        'data science': ['python', 'r', 'sql', 'machine learning', 'statistics'],
        'web development': ['javascript', 'react', 'node.js', 'databases'],
        'graphic design': ['photoshop', 'illustrator', 'branding', 'ui/ux'],
        'video editing': ['motion graphics', 'sound editing', 'storytelling', 'photography'],
        'social media': ['content creation', 'marketing', 'copywriting', 'analytics'],
        'fitness': ['nutrition', 'yoga', 'personal training', 'health coaching'],
    }
    
    complementary_skills = []
    
    # Find complements for user's existing skills
    for skill in user_skills:
        skill_lower = skill.lower()
        if skill_lower in skill_complements:
            complementary_skills.extend(skill_complements[skill_lower])
    
    # Remove duplicates and skills user already has or wants
    user_skills_lower = [s.lower() for s in user_skills]
    wanted_skills_lower = [s.lower() for s in wanted_skills]
    
    complementary_skills = list(set(complementary_skills))
    complementary_skills = [s for s in complementary_skills 
                          if s.lower() not in user_skills_lower 
                          and s.lower() not in wanted_skills_lower]
    
    return complementary_skills[:5]  # Return top 5 suggestions

def get_skill_categories() -> Dict[str, List[str]]:
    """
    Get predefined skill categories for better organization
    
    Returns:
        Dictionary mapping categories to skill lists
    """
    return {
        'Programming': [
            'python', 'javascript', 'java', 'c++', 'html', 'css', 'react', 
            'node.js', 'sql', 'git', 'docker', 'kubernetes'
        ],
        'Design': [
            'photoshop', 'illustrator', 'figma', 'sketch', 'ui/ux', 'graphic design',
            'web design', 'logo design', 'branding', 'typography'
        ],
        'Data & Analytics': [
            'data science', 'machine learning', 'excel', 'power bi', 'tableau',
            'statistics', 'r', 'data analysis', 'sql', 'big data'
        ],
        'Marketing': [
            'digital marketing', 'seo', 'social media', 'content marketing',
            'copywriting', 'email marketing', 'ppc', 'analytics'
        ],
        'Creative': [
            'photography', 'video editing', 'writing', 'drawing', 'painting',
            'music production', 'guitar', 'piano', 'singing'
        ],
        'Business': [
            'project management', 'leadership', 'sales', 'negotiation',
            'accounting', 'finance', 'consulting', 'strategy'
        ],
        'Languages': [
            'spanish', 'french', 'german', 'chinese', 'japanese', 'italian',
            'portuguese', 'translation', 'interpretation'
        ],
        'Health & Fitness': [
            'yoga', 'fitness', 'nutrition', 'meditation', 'personal training',
            'cooking', 'baking', 'health coaching'
        ],
        'Education': [
            'teaching', 'tutoring', 'curriculum design', 'e-learning',
            'presentation skills', 'public speaking', 'mentoring'
        ],
        'Technical': [
            'network administration', 'cybersecurity', 'cloud computing',
            'devops', 'system administration', 'troubleshooting'
        ]
    }

def categorize_skill(skill: str) -> str:
    """
    Categorize a skill based on predefined categories
    
    Args:
        skill: Skill to categorize
        
    Returns:
        Category name or 'Other' if not found
    """
    categories = get_skill_categories()
    skill_lower = skill.lower()
    
    for category, skills in categories.items():
        if skill_lower in [s.lower() for s in skills]:
            return category
    
    return 'Other'

def get_trending_skills() -> List[str]:
    """
    Get list of trending skills based on current market demand
    
    Returns:
        List of trending skills
    """
    return [
        'artificial intelligence',
        'machine learning',
        'data science',
        'cloud computing',
        'cybersecurity',
        'blockchain',
        'ui/ux design',
        'react',
        'python',
        'digital marketing',
        'content creation',
        'video editing',
        'remote work skills',
        'project management',
        'sustainability'
    ]

def suggest_learning_path(current_skills: List[str], target_skill: str) -> List[str]:
    """
    Suggest a learning path from current skills to target skill
    
    Args:
        current_skills: User's current skills
        target_skill: Skill user wants to learn
        
    Returns:
        List of intermediate skills to learn
    """
    # Skill progression paths
    learning_paths = {
        'machine learning': {
            'prerequisites': ['python', 'statistics', 'data analysis'],
            'intermediate': ['pandas', 'numpy', 'scikit-learn'],
            'advanced': ['tensorflow', 'pytorch', 'deep learning']
        },
        'web development': {
            'prerequisites': ['html', 'css'],
            'intermediate': ['javascript', 'responsive design'],
            'advanced': ['react', 'node.js', 'databases']
        },
        'data science': {
            'prerequisites': ['statistics', 'excel'],
            'intermediate': ['python', 'sql', 'data visualization'],
            'advanced': ['machine learning', 'big data', 'r']
        },
        'ui/ux design': {
            'prerequisites': ['design principles', 'psychology'],
            'intermediate': ['figma', 'prototyping', 'user research'],
            'advanced': ['interaction design', 'usability testing']
        },
        'digital marketing': {
            'prerequisites': ['marketing basics', 'content writing'],
            'intermediate': ['seo', 'social media', 'analytics'],
            'advanced': ['ppc', 'conversion optimization', 'marketing automation']
        }
    }
    
    target_lower = target_skill.lower()
    current_lower = [s.lower() for s in current_skills]
    
    if target_lower in learning_paths:
        path = learning_paths[target_lower]
        suggestions = []
        
        # Check prerequisites
        missing_prereqs = [s for s in path['prerequisites'] if s not in current_lower]
        if missing_prereqs:
            suggestions.extend(missing_prereqs)
        
        # Add intermediate skills
        suggestions.extend(path['intermediate'])
        
        # Filter out skills user already has
        suggestions = [s for s in suggestions if s not in current_lower]
        
        return suggestions[:5]  # Return top 5 suggestions
    
    return []