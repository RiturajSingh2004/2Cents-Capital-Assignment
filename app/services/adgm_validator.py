import os
import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.models import DocumentType, DocumentFlag, FlagSeverity, ComplianceCheck
from config import settings

class ADGMValidator:
    def __init__(self):
        self.chroma_client = None
        self.adgm_collection = None
        self._initialize_knowledge_base()
        
        # ADGM-specific validation rules
        self.validation_rules = self._load_validation_rules()
        self.mandatory_sections = self._load_mandatory_sections()
        
    def _initialize_knowledge_base(self):
        """Initialize ChromaDB for ADGM knowledge base"""
        try:
            # Create ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection for ADGM documents
            try:
                self.adgm_collection = self.chroma_client.get_collection("adgm_regulations")
            except ValueError:
                # Collection doesn't exist, create it
                self.adgm_collection = self.chroma_client.create_collection(
                    name="adgm_regulations",
                    metadata={"description": "ADGM regulations and compliance requirements"}
                )
                
                # Load initial ADGM knowledge if collection is empty
                self._load_initial_adgm_knowledge()
            
        except Exception as e:
            print(f"Failed to initialize ChromaDB: {str(e)}")
            # Fallback to memory-based validation
            self.chroma_client = None
            self.adgm_collection = None
    
    def _load_initial_adgm_knowledge(self):
        """Load basic ADGM knowledge into ChromaDB"""
        try:
            # Basic ADGM regulations (in production, load from official docs)
            adgm_knowledge = [
                {
                    "id": "companies_reg_1",
                    "document": "Companies Regulations 2020",
                    "content": "Every company incorporated in ADGM must have a registered office within ADGM jurisdiction.",
                    "section": "Registration Requirements",
                    "regulation_ref": "CR-2020-001"
                },
                {
                    "id": "companies_reg_2", 
                    "document": "Companies Regulations 2020",
                    "content": "Minimum share capital requirements vary by company type. Private companies require minimum AED 150,000.",
                    "section": "Share Capital",
                    "regulation_ref": "CR-2020-015"
                },
                {
                    "id": "companies_reg_3",
                    "document": "Companies Regulations 2020", 
                    "content": "All companies must maintain proper books of account and financial records as per ADGM accounting standards.",
                    "section": "Record Keeping",
                    "regulation_ref": "CR-2020-028"
                },
                {
                    "id": "aml_reg_1",
                    "document": "AML/CTF Regulations", 
                    "content": "All companies must implement adequate anti-money laundering procedures and customer due diligence.",
                    "section": "AML Compliance",
                    "regulation_ref": "AML-2020-005"
                },
                {
                    "id": "directors_reg_1",
                    "document": "Directors Regulations",
                    "content": "Every company must have at least one natural person director who is ordinarily resident in the UAE.",
                    "section": "Director Requirements", 
                    "regulation_ref": "DIR-2020-012"
                }
            ]
            
            # Add documents to collection
            documents = [item["content"] for item in adgm_knowledge]
            metadatas = [{k: v for k, v in item.items() if k != "content"} for item in adgm_knowledge]
            ids = [item["id"] for item in adgm_knowledge]
            
            self.adgm_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Loaded {len(adgm_knowledge)} ADGM regulation documents")
            
        except Exception as e:
            print(f"Failed to load ADGM knowledge: {str(e)}")
    
    def _load_validation_rules(self) -> Dict:
        """Load ADGM-specific validation rules"""
        return {
            "memorandum": {
                "required_clauses": [
                    "company name clause",
                    "registered office clause", 
                    "objects clause",
                    "liability clause",
                    "share capital clause"
                ],
                "prohibited_terms": [
                    "bank", "insurance", "islamic", "trust", "fund management"
                ],
                "format_requirements": {
                    "min_sections": 6,
                    "requires_signature": True,
                    "requires_date": True
                }
            },
            "articles": {
                "required_clauses": [
                    "share rights clause",
                    "director powers clause",
                    "meeting procedures clause", 
                    "dividend policy clause",
                    "transfer restrictions clause"
                ],
                "prohibited_terms": [],
                "format_requirements": {
                    "min_sections": 10,
                    "requires_signature": True,
                    "requires_date": True
                }
            },
            "application": {
                "required_fields": [
                    "company name",
                    "business activities",
                    "directors information",
                    "shareholders information",
                    "registered office"
                ],
                "validation_checks": [
                    "valid_activity_codes",
                    "director_qualifications", 
                    "capital_adequacy"
                ]
            },
            "board_resolution": {
                "required_elements": [
                    "meeting date",
                    "attendees list",
                    "resolutions passed",
                    "chairman signature"
                ],
                "format_requirements": {
                    "requires_quorum": True,
                    "requires_voting_record": True
                }
            }
        }
    
    def _load_mandatory_sections(self) -> Dict:
        """Load mandatory sections for each document type"""
        return {
            DocumentType.MEMORANDUM: [
                "Company Name",
                "Registered Office", 
                "Objects",
                "Share Capital",
                "Liability of Members",
                "Subscriber Details"
            ],
            DocumentType.ARTICLES: [
                "Share Classes and Rights",
                "Board of Directors",
                "General Meetings", 
                "Dividend Policy",
                "Transfer of Shares",
                "Accounts and Audit"
            ],
            DocumentType.APPLICATION: [
                "Company Details",
                "Business Activities",
                "Directors Information",
                "Shareholders Information", 
                "Financial Projections"
            ],
            DocumentType.BOARD_RESOLUTION: [
                "Meeting Details",
                "Attendees",
                "Resolutions",
                "Voting Record",
                "Signatures"
            ]
        }
    
    async def validate_document_compliance(self, content: str, doc_type: DocumentType, structure: Dict) -> List[ComplianceCheck]:
        """Main compliance validation function"""
        compliance_checks = []
        
        try:
            # Get mandatory sections for this document type
            mandatory_sections = self.mandatory_sections.get(doc_type, [])
            
            # Check each mandatory section
            for section in mandatory_sections:
                check = await self._validate_section(content, section, doc_type, structure)
                compliance_checks.append(check)
            
            # Perform document-specific validations
            specific_checks = await self._perform_specific_validations(content, doc_type)
            compliance_checks.extend(specific_checks)
            
            return compliance_checks
            
        except Exception as e:
            print(f"Compliance validation error: {str(e)}")
            return []
    
    async def _validate_section(self, content: str, section: str, doc_type: DocumentType, structure: Dict) -> ComplianceCheck:
        """Validate individual section compliance"""
        
        # Check if section exists in document
        present = self._section_exists(content, section, structure)
        
        # Get ADGM requirements for this section
        requirements = await self._get_section_requirements(section, doc_type)
        
        # Validate section content if present
        issues = []
        recommendations = []
        compliant = present
        
        if present:
            section_content = self._extract_section_content(content, section, structure)
            validation_result = await self._validate_section_content(
                section_content, section, doc_type, requirements
            )
            
            issues = validation_result.get('issues', [])
            recommendations = validation_result.get('recommendations', [])
            compliant = validation_result.get('compliant', False)
        else:
            issues.append(f"Required section '{section}' is missing")
            recommendations.append(f"Add {section} section as required by ADGM regulations")
        
        return ComplianceCheck(
            section=section,
            required=True,
            present=present,
            compliant=compliant,
            issues=issues,
            recommendations=recommendations
        )
    
    def _section_exists(self, content: str, section: str, structure: Dict) -> bool:
        """Check if section exists in document"""
        
        # Check in headings
        headings = structure.get('headings', [])
        for heading in headings:
            if section.lower() in heading.get('text', '').lower():
                return True
        
        # Check in content using keywords
        section_keywords = {
            "company name": ["name of", "company name", "corporate name"],
            "registered office": ["registered office", "principal office", "head office"],
            "objects": ["objects", "business objects", "company objects"],
            "share capital": ["share capital", "capital", "authorized capital"],
            "liability": ["liability", "member liability", "limited liability"],
            "directors": ["directors", "board", "management"],
            "meetings": ["meetings", "general meeting", "shareholders meeting"]
        }
        
        keywords = section_keywords.get(section.lower(), [section.lower()])
        content_lower = content.lower()
        
        return any(keyword in content_lower for keyword in keywords)
    
    async def _get_section_requirements(self, section: str, doc_type: DocumentType) -> Dict:
        """Get ADGM requirements for specific section"""
        
        if self.adgm_collection:
            try:
                # Query ChromaDB for relevant regulations
                results = self.adgm_collection.query(
                    query_texts=[f"{section} {doc_type.value} requirements"],
                    n_results=3
                )
                
                requirements = {
                    'regulations': results['documents'][0] if results['documents'] else [],
                    'references': results['metadatas'][0] if results['metadatas'] else []
                }
                
                return requirements
                
            except Exception as e:
                print(f"Error querying ADGM knowledge base: {str(e)}")
        
        # Fallback to hardcoded requirements
        return self._get_fallback_requirements(section, doc_type)
    
    def _get_fallback_requirements(self, section: str, doc_type: DocumentType) -> Dict:
        """Fallback requirements when ChromaDB is unavailable"""
        fallback_requirements = {
            "company name": {
                "must_include": ["Limited", "LLC", "PJSC"],
                "cannot_include": ["Bank", "Insurance"],
                "format": "Must end with appropriate legal suffix"
            },
            "registered office": {
                "must_include": ["ADGM", "Abu Dhabi"],
                "format": "Must be within ADGM jurisdiction"
            },
            "share capital": {
                "minimum": "AED 150,000 for private companies",
                "currency": "AED or USD accepted",
                "format": "Must specify authorized and issued capital"
            }
        }
        
        return fallback_requirements.get(section.lower(), {})
    
    def _extract_section_content(self, content: str, section: str, structure: Dict) -> str:
        """Extract content for specific section"""
        
        # Find section in structured content
        sections = structure.get('sections', [])
        for struct_section in sections:
            if section.lower() in struct_section.get('title', '').lower():
                return ' '.join(struct_section.get('content', []))
        
        # Fallback: extract using pattern matching
        lines = content.split('\n')
        section_content = []
        in_section = False
        
        for line in lines:
            if section.lower() in line.lower() and any(char in line for char in ':.-'):
                in_section = True
                section_content.append(line)
            elif in_section:
                if self._is_new_section_start(line):
                    break
                section_content.append(line)
        
        return '\n'.join(section_content)
    
    def _is_new_section_start(self, line: str) -> bool:
        """Check if line indicates start of new section"""
        indicators = ['article', 'section', 'clause', 'part', 'chapter']
        line_lower = line.lower().strip()
        
        # Check for numbered sections
        if re.match(r'^\d+\.', line_lower):
            return True
        
        # Check for section indicators
        return any(indicator in line_lower for indicator in indicators)
    
    async def _validate_section_content(self, content: str, section: str, doc_type: DocumentType, requirements: Dict) -> Dict:
        """Validate specific section content against requirements"""
        
        issues = []
        recommendations = []
        compliant = True
        
        # Validate based on section type
        if section.lower() == "company name":
            name_validation = self._validate_company_name(content)
            issues.extend(name_validation['issues'])
            recommendations.extend(name_validation['recommendations'])
            compliant = compliant and name_validation['compliant']
        
        elif section.lower() == "share capital":
            capital_validation = self._validate_share_capital(content)
            issues.extend(capital_validation['issues'])
            recommendations.extend(capital_validation['recommendations'])  
            compliant = compliant and capital_validation['compliant']
        
        elif section.lower() == "registered office":
            office_validation = self._validate_registered_office(content)
            issues.extend(office_validation['issues'])
            recommendations.extend(office_validation['recommendations'])
            compliant = compliant and office_validation['compliant']
        
        return {
            'compliant': compliant,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _validate_company_name(self, content: str) -> Dict:
        """Validate company name compliance"""
        issues = []
        recommendations = []
        compliant = True
        
        content_upper = content.upper()
        
        # Check for required legal suffix
        legal_suffixes = ['LIMITED', 'LTD', 'LLC', 'PJSC', 'PLC']
        has_suffix = any(suffix in content_upper for suffix in legal_suffixes)
        
        if not has_suffix:
            issues.append("Company name must include legal suffix (Limited, LLC, etc.)")
            recommendations.append("Add appropriate legal suffix to company name")
            compliant = False
        
        # Check for prohibited terms
        prohibited_terms = ['BANK', 'INSURANCE', 'ISLAMIC', 'TRUST']
        for term in prohibited_terms:
            if term in content_upper:
                issues.append(f"Company name contains prohibited term: {term}")
                recommendations.append(f"Remove or replace prohibited term: {term}")
                compliant = False
        
        return {
            'compliant': compliant,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _validate_share_capital(self, content: str) -> Dict:
        """Validate share capital compliance"""
        issues = []
        recommendations = []
        compliant = True
        
        # Extract capital amounts
        capital_pattern = r'(AED|USD)\s*([0-9,]+)'
        matches = re.findall(capital_pattern, content, re.IGNORECASE)
        
        if not matches:
            issues.append("Share capital amount not clearly specified")
            recommendations.append("Clearly specify share capital amount in AED or USD")
            compliant = False
        else:
            # Check minimum capital requirement (AED 150,000 for private companies)
            for currency, amount_str in matches:
                try:
                    amount = int(amount_str.replace(',', ''))
                    if currency.upper() == 'AED' and amount < 150000:
                        issues.append(f"Share capital {currency} {amount_str} below minimum requirement")
                        recommendations.append("Increase share capital to meet minimum AED 150,000 requirement")
                        compliant = False
                except ValueError:
                    issues.append("Invalid share capital amount format")
                    compliant = False
        
        return {
            'compliant': compliant,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _validate_registered_office(self, content: str) -> Dict:
        """Validate registered office compliance"""
        issues = []
        recommendations = []
        compliant = True
        
        content_upper = content.upper()
        
        # Check for ADGM jurisdiction
        adgm_indicators = ['ADGM', 'ABU DHABI GLOBAL MARKET', 'AL MARYAH ISLAND']
        has_adgm = any(indicator in content_upper for indicator in adgm_indicators)
        
        if not has_adgm:
            issues.append("Registered office must be within ADGM jurisdiction")
            recommendations.append("Specify registered office address within ADGM")
            compliant = False
        
        # Check for complete address
        address_components = ['FLOOR', 'BUILDING', 'STREET', 'P.O.', 'UAE']
        missing_components = [comp for comp in address_components if comp not in content_upper]
        
        if len(missing_components) > 2:
            issues.append("Incomplete registered office address")
            recommendations.append("Provide complete address including building, floor, and P.O. Box")
            compliant = False
        
        return {
            'compliant': compliant,
            'issues': issues,
            'recommendations': recommendations
        }
    
    async def _perform_specific_validations(self, content: str, doc_type: DocumentType) -> List[ComplianceCheck]:
        """Perform document-type specific validations"""
        specific_checks = []
        
        try:
            if doc_type == DocumentType.MEMORANDUM:
                specific_checks.extend(await self._validate_memorandum_specific(content))
            elif doc_type == DocumentType.ARTICLES:
                specific_checks.extend(await self._validate_articles_specific(content))
            elif doc_type == DocumentType.APPLICATION:
                specific_checks.extend(await self._validate_application_specific(content))
            elif doc_type == DocumentType.BOARD_RESOLUTION:
                specific_checks.extend(await self._validate_resolution_specific(content))
                
        except Exception as e:
            print(f"Specific validation error for {doc_type}: {str(e)}")
        
        return specific_checks
    
    async def _validate_memorandum_specific(self, content: str) -> List[ComplianceCheck]:
        """Memorandum-specific validations"""
        checks = []
        
        # Check for subscriber signatures
        signature_check = ComplianceCheck(
            section="Subscriber Signatures",
            required=True,
            present="signature" in content.lower() or "signed" in content.lower(),
            compliant=False,
            issues=[],
            recommendations=[]
        )
        
        if not signature_check.present:
            signature_check.issues.append("Subscriber signatures missing")
            signature_check.recommendations.append("Add subscriber signatures section")
        else:
            signature_check.compliant = True
        
        checks.append(signature_check)
        
        return checks
    
    async def _validate_articles_specific(self, content: str) -> List[ComplianceCheck]:
        """Articles-specific validations"""
        checks = []
        
        # Check for board composition
        board_check = ComplianceCheck(
            section="Board Composition",
            required=True,
            present="director" in content.lower() and "board" in content.lower(),
            compliant=False,
            issues=[],
            recommendations=[]
        )
        
        if board_check.present:
            # Check for minimum director requirement
            if "one director" in content.lower() or "1 director" in content.lower():
                board_check.compliant = True
            else:
                board_check.issues.append("Minimum director requirements not clearly specified")
                board_check.recommendations.append("Specify minimum number of directors")
        else:
            board_check.issues.append("Board composition not addressed")
            board_check.recommendations.append("Add board composition and director requirements")
        
        checks.append(board_check)
        
        return checks
    
    async def _validate_application_specific(self, content: str) -> List[ComplianceCheck]:
        """Application-specific validations"""  
        checks = []
        
        # Check for business activity codes
        activity_check = ComplianceCheck(
            section="Business Activities",
            required=True,
            present="activity" in content.lower() or "business" in content.lower(),
            compliant=False,
            issues=[],
            recommendations=[]
        )
        
        if activity_check.present:
            # Look for activity codes (simplified check)
            if re.search(r'\d{4,5}', content):
                activity_check.compliant = True
            else:
                activity_check.issues.append("Business activity codes not specified")
                activity_check.recommendations.append("Include specific ADGM business activity codes")
        else:
            activity_check.issues.append("Business activities section missing")
            activity_check.recommendations.append("Add detailed business activities description")
        
        checks.append(activity_check)
        
        return checks
    
    async def _validate_resolution_specific(self, content: str) -> List[ComplianceCheck]:
        """Board resolution-specific validations"""
        checks = []
        
        # Check for meeting quorum
        quorum_check = ComplianceCheck(
            section="Meeting Quorum",
            required=True,
            present="quorum" in content.lower() or "present" in content.lower(),
            compliant=False,
            issues=[],
            recommendations=[]
        )
        
        if quorum_check.present:
            quorum_check.compliant = True
        else:
            quorum_check.issues.append("Meeting quorum not confirmed")
            quorum_check.recommendations.append("Confirm meeting quorum was achieved")
        
        checks.append(quorum_check)
        
        return checks
    
    def calculate_compliance_score(self, compliance_checks: List[ComplianceCheck]) -> float:
        """Calculate overall compliance score"""
        if not compliance_checks:
            return 0.0
        
        total_checks = len(compliance_checks)
        compliant_checks = sum(1 for check in compliance_checks if check.compliant)
        
        return round((compliant_checks / total_checks) * 100, 2)
    
    def get_missing_documents_checklist(self, doc_type: DocumentType, uploaded_docs: List[str]) -> List[str]:
        """Get list of missing required documents for incorporation process"""
        
        incorporation_requirements = {
            DocumentType.APPLICATION: [
                "Company Registration Application",
                "Memorandum of Association", 
                "Articles of Association",
                "Board Resolution (if applicable)",
                "Passport copies of directors",
                "Proof of registered office"
            ]
        }
        
        required_docs = incorporation_requirements.get(doc_type, [])
        uploaded_doc_types = [doc.lower() for doc in uploaded_docs]
        
        missing_docs = []
        for required_doc in required_docs:
            if not any(req.lower() in uploaded for req in [required_doc] for uploaded in uploaded_doc_types):
                missing_docs.append(required_doc)
        
        return missing_docs