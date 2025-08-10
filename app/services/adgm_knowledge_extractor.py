"""
Minimal ADGM Knowledge Extractor 
"""

import os
import json
import asyncio
import aiohttp
import chromadb
from chromadb.config import Settings as ChromaSettings
from pathlib import Path
from typing import Dict, List, Optional
import re
from datetime import datetime
import logging

class ADGMKnowledgeExtractor:
    def __init__(self, chroma_db_path: str = "./data/chroma_db"):
        self.chroma_db_path = chroma_db_path
        self.chroma_client = None
        self.adgm_collection = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Your ADGM knowledge data
        self.enhanced_adgm_knowledge = [
            {
                "id": "companies_reg_001",
                "document": "Companies Regulations 2020",
                "content": "Every company incorporated in ADGM must have a registered office within ADGM jurisdiction at Al Maryah Island, Abu Dhabi.",
                "section": "Registration Requirements",
                "regulation_ref": "CR-2020-001",
                "category": "incorporation",
                "keywords": ["registered office", "jurisdiction", "incorporation", "ADGM"]
            },
            {
                "id": "companies_reg_002",
                "document": "Companies Regulations 2020", 
                "content": "Private companies require minimum authorized share capital of AED 150,000. Public companies require minimum AED 2,000,000.",
                "section": "Share Capital Requirements",
                "regulation_ref": "CR-2020-015",
                "category": "capital",
                "keywords": ["share capital", "minimum capital", "private company", "public company", "AED"]
            },
            {
                "id": "companies_reg_003",
                "document": "Companies Regulations 2020",
                "content": "All companies must maintain proper books of account and financial records in accordance with IFRS and ADGM accounting standards.",
                "section": "Record Keeping & Accounting",
                "regulation_ref": "CR-2020-028",
                "category": "compliance",
                "keywords": ["books of account", "financial records", "IFRS", "accounting standards"]
            },
            {
                "id": "memorandum_req_001",
                "document": "Memorandum Requirements Guide",
                "content": "Memorandum of Association must include: company name clause, registered office clause, objects clause, liability clause, and share capital clause with subscriber details.",
                "section": "Memorandum Content",
                "regulation_ref": "MEM-2020-001",
                "category": "memorandum",
                "keywords": ["memorandum", "company name clause", "objects clause", "liability clause", "subscribers"]
            },
            {
                "id": "articles_req_001",
                "document": "Articles Requirements Guide",
                "content": "Articles of Association must contain provisions for share rights, director powers, meeting procedures, dividend policy, and share transfer restrictions.",
                "section": "Articles Content",
                "regulation_ref": "ART-2020-001",
                "category": "articles",
                "keywords": ["articles", "share rights", "director powers", "meetings", "dividends", "transfer restrictions"]
            },
            {
                "id": "directors_req_001",
                "document": "Directors Regulations 2020",
                "content": "Every company must have at least one natural person director who is ordinarily resident in the UAE or holds UAE residency visa.",
                "section": "Director Requirements",
                "regulation_ref": "DIR-2020-012",
                "category": "governance",
                "keywords": ["directors", "natural person", "UAE resident", "residency visa"]
            },
            {
                "id": "company_names_001",
                "document": "Company Names Regulations",
                "content": "Company names must end with appropriate legal suffix: Limited/Ltd for private companies, PLC for public companies, or LLC for limited liability companies. Cannot contain prohibited words: Bank, Insurance, Islamic (unless licensed), Trust, Fund Management.",
                "section": "Company Name Requirements",
                "regulation_ref": "CN-2020-008",
                "category": "incorporation",
                "keywords": ["company name", "legal suffix", "Limited", "LLC", "PLC", "prohibited names"]
            },
            {
                "id": "aml_req_001",
                "document": "AML/CTF Regulations 2020",
                "content": "All ADGM companies must implement adequate anti-money laundering procedures, customer due diligence, and beneficial ownership identification.",
                "section": "AML Compliance",
                "regulation_ref": "AML-2020-005",
                "category": "compliance",
                "keywords": ["AML", "anti-money laundering", "customer due diligence", "beneficial ownership"]
            },
            {
                "id": "board_resolution_001",
                "document": "Board Resolution Requirements",
                "content": "Board resolutions must record meeting date, attendees, quorum confirmation, resolutions passed with voting details, and chairman signature.",
                "section": "Board Resolution Format",
                "regulation_ref": "BR-2020-001",
                "category": "governance",
                "keywords": ["board resolution", "meeting date", "quorum", "voting", "chairman signature"]
            },
            {
                "id": "application_req_001",
                "document": "Application Requirements Guide",
                "content": "Registration applications must include complete company details, business activities with ADGM codes, directors information, shareholders details, and financial projections.",
                "section": "Application Requirements",
                "regulation_ref": "APP-2020-001",
                "category": "application",
                "keywords": ["application", "business activities", "ADGM codes", "directors information", "shareholders", "financial projections"]
            }
        ]
    
    async def initialize_knowledge_base(self):
        """Initialize ChromaDB and populate with ADGM knowledge"""
        try:
            # Ensure directory exists
            Path(self.chroma_db_path).mkdir(parents=True, exist_ok=True)
            
            # Create ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_db_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create or get ADGM collection
            try:
                self.adgm_collection = self.chroma_client.get_collection("adgm_regulations")
                self.logger.info("Retrieved existing ADGM collection")
            except ValueError:
                self.adgm_collection = self.chroma_client.create_collection(
                    name="adgm_regulations",
                    metadata={"description": "ADGM regulations and compliance requirements"}
                )
                self.logger.info("Created new ADGM collection")
            
            # Populate with knowledge
            await self.populate_knowledge()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize knowledge base: {str(e)}")
            return False
    
    async def populate_knowledge(self):
        """Populate knowledge base with ADGM data"""
        try:
            # Clear existing data (optional - remove if you want to keep existing)
            # self.adgm_collection.delete()
            
            documents = []
            metadatas = []
            ids = []
            
            for item in self.enhanced_adgm_knowledge:
                documents.append(item['content'])
                metadatas.append({
                    'document': item['document'],
                    'section': item['section'],
                    'regulation_ref': item['regulation_ref'],
                    'category': item['category'],
                    'keywords': item['keywords'],
                    'source_type': 'enhanced_knowledge'
                })
                ids.append(item['id'])
            
            # Add to collection
            if documents:
                self.adgm_collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                self.logger.info(f"Added {len(documents)} ADGM knowledge documents")
            
        except Exception as e:
            self.logger.error(f"Failed to populate knowledge: {str(e)}")
    
    def query_knowledge_base(self, query: str, n_results: int = 5) -> Dict:
        """Query the ADGM knowledge base"""
        try:
            if not self.adgm_collection:
                return {"error": "Knowledge base not initialized"}
            
            results = self.adgm_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            return {
                "query": query,
                "results": results,
                "count": len(results['documents'][0]) if results['documents'] else 0
            }
        
        except Exception as e:
            return {"error": f"Query failed: {str(e)}"}
    
    def get_knowledge_stats(self) -> Dict:
        """Get knowledge base statistics"""
        try:
            if not self.adgm_collection:
                return {"error": "Knowledge base not initialized"}
            
            total_count = self.adgm_collection.count()
            
            return {
                "total_documents": total_count,
                "last_updated": datetime.now().isoformat(),
                "status": "operational"
            }
        
        except Exception as e:
            return {"error": f"Stats retrieval failed: {str(e)}"}