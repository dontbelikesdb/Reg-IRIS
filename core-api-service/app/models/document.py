import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class DocumentFamily(Base):
    __tablename__ = "document_families"

    family_id = Column(String(100), primary_key=True)
    title = Column(String(255), nullable=False)
    regulator = Column(String(50), nullable=False, index=True)      # ESMA, SEC, FCA, CFTC
    jurisdiction = Column(String(50), nullable=False, index=True)   # EU, US, UK
    category = Column(String(100), nullable=False, index=True)      # Reporting, Clearing
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("RegulatoryDocument", back_populates="family")
    diffs = relationship("WhatsNewDiff", back_populates="family")


class RegulatoryDocument(Base):
    __tablename__ = "regulatory_documents"

    doc_id = Column(String(100), primary_key=True)
    family_id = Column(String(100), ForeignKey("document_families.family_id"), nullable=False)
    version_label = Column(String(20), nullable=False)             # v1.0, v1.1, v2.0
    parent_doc_id = Column(String(100), nullable=True)            # Links v2 to v1
    
    # Bitemporal Anchors
    published_at = Column(Date, nullable=True)
    effective_from = Column(Date, nullable=True, index=True)
    effective_to = Column(Date, nullable=True, index=True)
    status = Column(String(30), default="ACTIVE", index=True)      # ACTIVE, SUPERSEDED, FUTURE_EFFECTIVE
    
    # Metadata Discrepancy & File Info
    has_metadata_conflict = Column(Boolean, default=False)
    metadata_warning_note = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)

    family = relationship("DocumentFamily", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id = Column(String(150), primary_key=True)
    doc_id = Column(String(100), ForeignKey("regulatory_documents.doc_id"), nullable=False)
    
    # Hierarchical context
    parent_section_id = Column(String(100), nullable=True)
    parent_header = Column(String(255), nullable=True)
    clause_reference = Column(String(100), nullable=True)          # e.g. "Paragraph 3"
    page_number = Column(Integer, nullable=False, index=True)      # For clickable citations
    
    # Sibling Links
    prev_chunk_id = Column(String(150), nullable=True)
    next_chunk_id = Column(String(150), nullable=True)
    
    content = Column(Text, nullable=False)
    is_contaminated = Column(Boolean, default=False)               # Flags stray text (e.g. EMIR v2 p.3)

    document = relationship("RegulatoryDocument", back_populates="chunks")


class WhatsNewDiff(Base):
    __tablename__ = "whats_new_diffs"

    diff_id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    family_id = Column(String(100), ForeignKey("document_families.family_id"), nullable=False)
    from_version = Column(String(20), nullable=False)
    to_version = Column(String(20), nullable=False)
    effective_date = Column(Date, nullable=False)
    diff_summary = Column(Text, nullable=False)
    added_clauses_count = Column(Integer, default=0)
    modified_clauses_count = Column(Integer, default=0)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    family = relationship("DocumentFamily", back_populates="diffs")