"""Guardrails service for content safety and fallback logic"""
from typing import Tuple, Optional, Dict, Any
from app.config import settings
import re


class GuardrailsService:
    """Service for implementing guardrails and safety checks"""
    
    def __init__(self):
        self.toxicity_patterns = [
            r'\b(hate|violence|harmful)\b',
            # Add more patterns as needed
        ]
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        }
    
    async def check_input(self, text: str) -> Tuple[bool, Optional[str]]:
        """Check if input passes guardrails"""
        if not settings.GUARDRAILS_ENABLED:
            return True, None
        
        # Check for toxicity
        toxicity_score = self._check_toxicity(text)
        if toxicity_score > settings.GUARDRAILS_MAX_TOXICITY_SCORE:
            return False, "Input contains inappropriate content"
        
        # Check for PII if enabled
        if settings.GUARDRAILS_MAX_PII_DETECTION:
            pii_found = self._detect_pii(text)
            if pii_found:
                return False, "Input contains potentially sensitive information"
        
        return True, None
    
    async def check_output(self, text: str) -> Tuple[bool, Optional[str]]:
        """Check if output passes guardrails"""
        if not settings.GUARDRAILS_ENABLED:
            return True, None
        
        # Check for toxicity
        toxicity_score = self._check_toxicity(text)
        if toxicity_score > settings.GUARDRAILS_MAX_TOXICITY_SCORE:
            if settings.GUARDRAILS_FALLBACK_ENABLED:
                return False, "Response filtered due to content policy"
            return False, "Response contains inappropriate content"
        
        # Check for PII if enabled
        if settings.GUARDRAILS_MAX_PII_DETECTION:
            pii_found = self._detect_pii(text)
            if pii_found:
                return False, "Response contains potentially sensitive information"
        
        return True, None
    
    def _check_toxicity(self, text: str) -> float:
        """Simple toxicity check (can be enhanced with ML models)"""
        text_lower = text.lower()
        matches = sum(1 for pattern in self.toxicity_patterns if re.search(pattern, text_lower, re.IGNORECASE))
        # Normalize to 0-1 scale
        return min(matches / len(self.toxicity_patterns), 1.0) if self.toxicity_patterns else 0.0
    
    def _detect_pii(self, text: str) -> bool:
        """Detect personally identifiable information"""
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, text):
                return True
        return False
    
    async def apply_fallback(self, error: Exception, context: Dict[str, Any]) -> str:
        """Apply fallback logic when errors occur"""
        if not settings.GUARDRAILS_FALLBACK_ENABLED:
            raise error
        
        error_type = type(error).__name__
        
        # Fallback responses based on error type
        fallback_responses = {
            "TimeoutError": "I'm taking longer than expected. Please try again with a simpler query.",
            "RateLimitError": "I'm experiencing high demand. Please try again in a moment.",
            "ValueError": "I couldn't understand that request. Could you rephrase it?",
            "KeyError": "Some required information is missing. Please check your input.",
        }
        
        return fallback_responses.get(
            error_type,
            "An error occurred. Please try again or rephrase your question."
        )
    
    def sanitize_output(self, text: str) -> str:
        """Sanitize output by removing detected PII"""
        sanitized = text
        for pii_type, pattern in self.pii_patterns.items():
            sanitized = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", sanitized)
        return sanitized

