"""
Enhanced ADGM Validator with Knowledge Base Integration
Minimal integration with existing ADGMValidator
"""

from .adgm_validator import ADGMValidator
from .adgm_knowledge_extractor import ADGMKnowledgeExtractor
from app.models import DocumentType, ComplianceCheck
from typing import List, Dict
import asyncio

class EnhancedADGMValidator(ADGMValidator):
    """Enhanced ADGM Validator with knowledge base integration"""
    
    def __init__(self):
        super().__init__()
        self.knowledge_extractor = ADGMKnowledgeExtractor()
        self.knowledge_initialized = False
    
    async def initialize_knowledge_base(self):
        """Initialize the knowledge base (call this once on startup)"""
        try:
            success = await self.knowledge_extractor.initialize_knowledge_base()
            if success:
                # Update the parent class collection reference
                self.adgm_collection = self.knowledge_extractor.adgm_collection
                self.knowledge_initialized = True
                print("✅ Enhanced ADGM knowledge base initialized")
                return True
            else:
                print("⚠️ Knowledge base initialization failed, using fallback mode")
                return False
        except Exception as e:
            print(f"⚠️ Knowledge base error: {str(e)}, using fallback mode")
            return False
    
    async def enhanced_validate_document_compliance(self, content: str, doc_type: DocumentType, structure: Dict) -> List[ComplianceCheck]:
        """Enhanced validation using knowledge base"""
        
        # Start with base validation from parent class
        base_checks = await super().validate_document_compliance(content, doc_type, structure)
        
        # If knowledge base is available, add enhanced checks
        if self.knowledge_initialized:
            enhanced_checks = await self._knowledge_base_validation(content, doc_type)
            base_checks.extend(enhanced_checks)
        
        return base_checks
    
    async def _knowledge_base_validation(self, content: str, doc_type: DocumentType) -> List[ComplianceCheck]:
        """Validate against knowledge base"""
        checks = []
        
        try:
            # Query knowledge base for document-specific requirements
            doc_type_value = doc_type.value if hasattr(doc_type, 'value') else str(doc_type)
            
            query_result = self.knowledge_extractor.query_knowledge_base(
                f"{doc_type_value} requirements ADGM", 
                n_results=5
            )
            
            if query_result.get('results') and query_result['results']['documents']:
                kb_documents = query_result['results']['documents'][0]
                kb_metadata = query_result['results']['metadatas'][0]
                
                # Check content against knowledge base requirements
                for doc_text, metadata in zip(kb_documents, kb_metadata):
                    if self._content_missing_requirement(content, doc_text):
                        check = ComplianceCheck(
                            section=f"KB Check: {metadata.get('section', 'Unknown')}",
                            required=False,
                            present=False,
                            compliant=False,
                            issues=[f"May be missing: {doc_text[:100]}..."],
                            recommendations=[f"Review {metadata.get('regulation_ref', 'regulation')}"]
                        )
                        checks.append(check)
        
        except Exception as e:
            print(f"Knowledge base validation error: {str(e)}")
        
        return checks
    
    def _content_missing_requirement(self, content: str, requirement_text: str) -> bool:
        """Simple check if content might be missing a requirement"""
        # Extract key terms from requirement
        key_terms = self._extract_key_terms(requirement_text)
        content_lower = content.lower()
        
        # If less than 30% of key terms are found, flag as potentially missing
        found_terms = sum(1 for term in key_terms if term.lower() in content_lower)
        return found_terms < len(key_terms) * 0.3
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract important terms from requirement text"""
        # Simple extraction of important nouns/terms
        import re
        words = re.findall(r'\b[A-Za-z]{4,}\b', text)
        
        # Filter out common words
        common_words = {'must', 'shall', 'should', 'include', 'contain', 'company', 'adgm'}
        key_terms = [word for word in words if word.lower() not in common_words]
        
        return list(set(key_terms))[:5]  # Top 5 unique terms
    
    async def get_knowledge_requirements(self, section: str, doc_type: str) -> Dict:
        """Get requirements from knowledge base for specific section"""
        if not self.knowledge_initialized:
            return await super()._get_section_requirements(section, doc_type)
        
        try:
            query_result = self.knowledge_extractor.query_knowledge_base(
                f"{section} {doc_type} requirements", 
                n_results=3
            )
            
            if query_result.get('results') and query_result['results']['documents']:
                return {
                    'regulations': query_result['results']['documents'][0],
                    'references': query_result['results']['metadatas'][0],
                    'source': 'knowledge_base'
                }
        except Exception as e:
            print(f"Error querying knowledge base: {str(e)}")
        
        # Fallback to parent method
        return await super()._get_section_requirements(section, doc_type)