"""
Content moderation using AI to detect spam, toxicity, and inappropriate content
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModerationResult:
    """Result of content moderation"""
    is_flagged: bool
    confidence: float
    categories: List[str]
    reason: str
    cleaned_content: Optional[str] = None

class ContentModerator:
    """
    AI-powered content moderation system
    """
    
    def __init__(self):
        """Initialize the content moderator"""
        self.spam_keywords = self._load_spam_keywords()
        self.toxic_patterns = self._load_toxic_patterns()
        self.detoxify_model = None
        self._load_detoxify_model()
    
    def _load_detoxify_model(self):
        """Load the Detoxify model for toxicity detection"""
        try:
            from detoxify import Detoxify
            self.detoxify_model = Detoxify('original')
            logger.info("Loaded Detoxify model successfully")
        except ImportError:
            logger.warning("Detoxify not available, using rule-based detection only")
            self.detoxify_model = None
        except Exception as e:
            logger.error(f"Failed to load Detoxify model: {e}")
            self.detoxify_model = None
    
    def _load_spam_keywords(self) -> List[str]:
        """Load spam keywords and patterns"""
        return [
            # Promotional spam
            'make money', 'get rich', 'work from home', 'easy money',
            'guaranteed income', 'no experience needed', 'click here',
            'free money', 'earn cash', 'passive income',
            
            # Contact spam
            'contact me', 'email me', 'call me', 'whatsapp',
            'telegram', 'discord', 'skype', 'zoom meeting',
            
            # Suspicious offers
            'too good to be true', 'limited time', 'act now',
            'special offer', 'exclusive deal', 'secret method',
            
            # Irrelevant content
            'buy now', 'sale', 'discount', 'promo code',
            'affiliate', 'referral', 'commission',
            
            # Inappropriate skill descriptions
            'adult content', 'xxx', 'mature', 'nsfw',
            'dating', 'romance', 'relationship advice',
        ]
    
    def _load_toxic_patterns(self) -> List[str]:
        """Load toxic language patterns"""
        return [
            # Hate speech indicators
            r'\b(hate|despise|loathe)\b.*\b(people|person|group)\b',
            r'\b(stupid|dumb|idiotic|moronic)\b.*\b(people|person)\b',
            
            # Discrimination patterns
            r'\b(all|every)\b.*\b(women|men|girls|boys)\b.*\b(are|should)\b',
            r'\b(no|never)\b.*\b(hire|work with|teach)\b.*\b(women|men)\b',
            
            # Threatening language
            r'\b(kill|hurt|harm|destroy)\b',
            r'\b(threat|threaten|intimidate)\b',
            
            # Harassment patterns
            r'\b(harass|stalk|follow)\b',
            r'\b(creep|creepy|weird)\b.*\b(message|contact)\b',
        ]
    
    def moderate_content(self, content: str, content_type: str = 'general') -> ModerationResult:
        """
        Moderate content for spam, toxicity, and appropriateness
        
        Args:
            content: Text content to moderate
            content_type: Type of content ('skill', 'message', 'profile', 'general')
            
        Returns:
            ModerationResult with flagging decision and details
        """
        if not content or not content.strip():
            return ModerationResult(
                is_flagged=False,
                confidence=0.0,
                categories=[],
                reason="Empty content"
            )
        
        content = content.strip()
        flagged_categories = []
        max_confidence = 0.0
        reasons = []
        
        # 1. Check for spam
        spam_result = self._check_spam(content)
        if spam_result['is_spam']:
            flagged_categories.append('spam')
            max_confidence = max(max_confidence, spam_result['confidence'])
            reasons.append(spam_result['reason'])
        
        # 2. Check for toxic content
        toxic_result = self._check_toxicity(content)
        if toxic_result['is_toxic']:
            flagged_categories.append('toxic')
            max_confidence = max(max_confidence, toxic_result['confidence'])
            reasons.append(toxic_result['reason'])
        
        # 3. Check for inappropriate content
        inappropriate_result = self._check_inappropriate(content, content_type)
        if inappropriate_result['is_inappropriate']:
            flagged_categories.append('inappropriate')
            max_confidence = max(max_confidence, inappropriate_result['confidence'])
            reasons.append(inappropriate_result['reason'])
        
        # 4. Check for suspicious patterns
        suspicious_result = self._check_suspicious_patterns(content)
        if suspicious_result['is_suspicious']:
            flagged_categories.append('suspicious')
            max_confidence = max(max_confidence, suspicious_result['confidence'])
            reasons.append(suspicious_result['reason'])
        
        is_flagged = len(flagged_categories) > 0
        combined_reason = '; '.join(reasons) if reasons else "Content passed moderation"
        
        return ModerationResult(
            is_flagged=is_flagged,
            confidence=max_confidence,
            categories=flagged_categories,
            reason=combined_reason,
            cleaned_content=self._clean_content(content) if not is_flagged else None
        )
    
    def _check_spam(self, content: str) -> Dict:
        """Check for spam content"""
        content_lower = content.lower()
        
        # Count spam keywords
        spam_count = 0
        matched_keywords = []
        
        for keyword in self.spam_keywords:
            if keyword in content_lower:
                spam_count += 1
                matched_keywords.append(keyword)
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}',  # URLs
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email addresses
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
            r'\$\d+',  # Dollar amounts
            r'\b(FREE|EARN|MAKE)\b.*\$\d+',  # Free money offers
        ]
        
        pattern_matches = 0
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                pattern_matches += 1
        
        # Calculate spam confidence
        total_words = len(content.split())
        spam_ratio = spam_count / max(total_words, 1)
        
        # Determine if spam
        is_spam = (spam_count >= 2 or 
                  spam_ratio > 0.3 or 
                  pattern_matches >= 2)
        
        confidence = min(spam_ratio * 2 + pattern_matches * 0.3, 1.0)
        
        reason = ""
        if spam_count > 0:
            reason += f"Contains spam keywords: {', '.join(matched_keywords[:3])}"
        if pattern_matches > 0:
            reason += f"{'; ' if reason else ''}Contains suspicious patterns"
        
        return {
            'is_spam': is_spam,
            'confidence': confidence,
            'reason': reason or "No spam detected"
        }
    
    def _check_toxicity(self, content: str) -> Dict:
        """Check for toxic content using AI and rules"""
        # Use Detoxify if available
        if self.detoxify_model:
            try:
                results = self.detoxify_model.predict(content)
                
                # Check various toxicity categories
                toxicity_scores = {
                    'toxicity': results.get('toxicity', 0),
                    'severe_toxicity': results.get('severe_toxicity', 0),
                    'obscene': results.get('obscene', 0),
                    'threat': results.get('threat', 0),
                    'insult': results.get('insult', 0),
                    'identity_attack': results.get('identity_attack', 0)
                }
                
                max_score = max(toxicity_scores.values())
                
                # Determine if toxic (lower threshold for skill platform)
                is_toxic = (toxicity_scores['toxicity'] > 0.6 or
                           toxicity_scores['severe_toxicity'] > 0.3 or
                           toxicity_scores['threat'] > 0.5 or
                           toxicity_scores['insult'] > 0.5 or
                           toxicity_scores['identity_attack'] > 0.5)
                
                flagged_categories = [k for k, v in toxicity_scores.items() if v > 0.5]
                
                return {
                    'is_toxic': is_toxic,
                    'confidence': max_score,
                    'reason': f"AI detected: {', '.join(flagged_categories)}" if flagged_categories else "No toxicity detected"
                }
            
            except Exception as e:
                logger.error(f"Detoxify prediction failed: {e}")
        
        # Fallback to rule-based detection
        return self._check_toxicity_rules(content)
    
    def _check_toxicity_rules(self, content: str) -> Dict:
        """Rule-based toxicity detection"""
        content_lower = content.lower()
        
        # Check for toxic patterns
        toxic_matches = 0
        matched_patterns = []
        
        for pattern in self.toxic_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                toxic_matches += 1
                matched_patterns.append(pattern)
        
        # Check for explicit profanity (basic list)
        profanity_list = [
            'damn', 'hell', 'stupid', 'idiot', 'moron', 'dumb',
            'hate', 'kill', 'die', 'loser', 'pathetic'
        ]
        
        profanity_count = sum(1 for word in profanity_list if word in content_lower)
        
        is_toxic = toxic_matches > 0 or profanity_count >= 2
        confidence = min((toxic_matches * 0.4) + (profanity_count * 0.2), 1.0)
        
        reason = ""
        if toxic_matches > 0:
            reason += f"Contains toxic language patterns"
        if profanity_count > 0:
            reason += f"{'; ' if reason else ''}Contains {profanity_count} potentially offensive words"
        
        return {
            'is_toxic': is_toxic,
            'confidence': confidence,
            'reason': reason or "No toxicity detected"
        }
    
    def _check_inappropriate(self, content: str, content_type: str) -> Dict:
        """Check for inappropriate content based on context"""
        content_lower = content.lower()
        
        inappropriate_keywords = {
            'adult': ['adult', 'mature', 'nsfw', 'xxx', '18+', 'explicit'],
            'dating': ['dating', 'romance', 'hookup', 'singles', 'flirt'],
            'financial': ['bitcoin', 'crypto', 'investment', 'trading', 'forex'],
            'medical': ['medical advice', 'diagnosis', 'prescription', 'treatment'],
            'legal': ['legal advice', 'lawyer', 'lawsuit', 'litigation'],
            'religious': ['convert', 'salvation', 'prophet', 'blessed'],
            'political': ['vote for', 'election', 'candidate', 'political party']
        }
        
        if content_type == 'skill':
            # Skills should be professional and educational
            inappropriate_categories = ['adult', 'dating']
        else:
            # Messages can be more flexible but still appropriate
            inappropriate_categories = ['adult']
        
        flagged_categories = []
        total_matches = 0
        
        for category in inappropriate_categories:
            if category in inappropriate_keywords:
                matches = sum(1 for keyword in inappropriate_keywords[category] 
                            if keyword in content_lower)
                if matches > 0:
                    flagged_categories.append(category)
                    total_matches += matches
        
        is_inappropriate = len(flagged_categories) > 0
        confidence = min(total_matches * 0.3, 1.0)
        
        reason = f"Contains inappropriate content: {', '.join(flagged_categories)}" if flagged_categories else "Content is appropriate"
        
        return {
            'is_inappropriate': is_inappropriate,
            'confidence': confidence,
            'reason': reason
        }
    
    def _check_suspicious_patterns(self, content: str) -> Dict:
        """Check for suspicious patterns that might indicate spam or scams"""
        suspicious_patterns = [
            r'\b(guaranteed|100%|promise)\b.*\b(money|income|profit)\b',
            r'\b(no risk|risk free|safe investment)\b',
            r'\b(limited time|act now|hurry)\b',
            r'\b(secret|hidden|exclusive)\b.*\b(method|technique|system)\b',
            r'\b(make \$\d+|earn \$\d+)\b.*\b(daily|weekly|monthly)\b',
            r'\b(work from home|remote work)\b.*\b(easy|simple|no experience)\b',
            r'[A-Z]{3,}.*[A-Z]{3,}.*[A-Z]{3,}',  # Excessive caps
            r'(.)\1{4,}',  # Repeated characters
            r'(.)(.)\1\2{3,}',  # Alternating repeated patterns
        ]
        
        pattern_matches = 0
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                pattern_matches += 1
        
        # Check for excessive punctuation or emojis
        punctuation_ratio = len(re.findall(r'[!?]{2,}', content)) / max(len(content), 1)
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content))
        
        is_suspicious = (pattern_matches >= 2 or 
                        punctuation_ratio > 0.1 or 
                        emoji_count > 10)
        
        confidence = min(pattern_matches * 0.3 + punctuation_ratio * 2 + emoji_count * 0.05, 1.0)
        
        reason = ""
        if pattern_matches > 0:
            reason += f"Contains {pattern_matches} suspicious patterns"
        if punctuation_ratio > 0.1:
            reason += f"{'; ' if reason else ''}Excessive punctuation"
        if emoji_count > 10:
            reason += f"{'; ' if reason else ''}Excessive emojis ({emoji_count})"
        
        return {
            'is_suspicious': is_suspicious,
            'confidence': confidence,
            'reason': reason or "No suspicious patterns detected"
        }
    
    def _clean_content(self, content: str) -> str:
        """Clean content by removing or replacing problematic elements"""
        # Remove excessive punctuation
        content = re.sub(r'[!?]{3,}', '!', content)
        
        # Remove excessive caps (but keep acronyms)
        words = content.split()
        cleaned_words = []
        for word in words:
            if len(word) > 3 and word.isupper() and word.isalpha():
                cleaned_words.append(word.lower().capitalize())
            else:
                cleaned_words.append(word)
        
        content = ' '.join(cleaned_words)
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content

# Global moderator instance
_moderator = None

def get_moderator() -> ContentModerator:
    """Get the global content moderator instance"""
    global _moderator
    if _moderator is None:
        _moderator = ContentModerator()
    return _moderator

def is_spammy(content: str) -> bool:
    """
    Quick check if content is spammy
    
    Args:
        content: Content to check
        
    Returns:
        True if content is flagged as spam
    """
    if not content:
        return False
    
    moderator = get_moderator()
    result = moderator.moderate_content(content)
    
    return result.is_flagged and ('spam' in result.categories or 'suspicious' in result.categories)

def moderate_content(content: str, content_type: str = 'general') -> ModerationResult:
    """
    Moderate content for all issues
    
    Args:
        content: Content to moderate
        content_type: Type of content
        
    Returns:
        ModerationResult with detailed analysis
    """
    moderator = get_moderator()
    return moderator.moderate_content(content, content_type)

def is_appropriate_skill(skill_description: str) -> bool:
    """
    Check if a skill description is appropriate for the platform
    
    Args:
        skill_description: Skill description to check
        
    Returns:
        True if skill is appropriate
    """
    result = moderate_content(skill_description, 'skill')
    return not result.is_flagged

def clean_user_input(content: str) -> str:
    """
    Clean user input while preserving meaning
    
    Args:
        content: Raw user input
        
    Returns:
        Cleaned content
    """
    moderator = get_moderator()
    return moderator._clean_content(content)