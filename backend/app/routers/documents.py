from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentSection, Paragraph, Sentence
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse,
    SectionResponse, SectionUpdateStatus,
    ParagraphResponse, ParagraphUpdate,
    SentenceResponse
)

router = APIRouter()


@router.get("/", response_model=List[DocumentListResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents for the current user"""
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new document"""
    new_document = Document(
        user_id=current_user.id,
        title=document_data.title,
        content_full=document_data.content_full,
        goal_id=document_data.goal_id,
        word_count=len(document_data.content_full.split()) if document_data.content_full else 0
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    return new_document


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update fields
    if document_data.title is not None:
        document.title = document_data.title
    if document_data.content_full is not None:
        document.content_full = document_data.content_full
        document.word_count = len(document_data.content_full.split())
        document.version += 1
    if document_data.goal_id is not None:
        document.goal_id = document_data.goal_id
    
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    db.delete(document)
    db.commit()
    return None


# Section endpoints
@router.get("/{document_id}/sections", response_model=List[SectionResponse])
def list_document_sections(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve sections and completion state for a document"""
    # Verify document ownership
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    sections = db.query(DocumentSection).filter(
        DocumentSection.document_id == document_id
    ).order_by(DocumentSection.order_index).all()
    
    return sections


@router.put("/{document_id}/sections/{section_id}", response_model=SectionResponse)
def update_section_status(
    document_id: UUID,
    section_id: UUID,
    section_data: SectionUpdateStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark section as complete/incomplete"""
    # Verify document ownership
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    section = db.query(DocumentSection).filter(
        DocumentSection.id == section_id,
        DocumentSection.document_id == document_id
    ).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    section.is_complete = section_data.is_complete
    db.commit()
    db.refresh(section)
    return section


# Paragraph endpoints
@router.get("/{document_id}/paragraphs", response_model=List[ParagraphResponse])
def get_document_paragraphs(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve structured paragraphs with text and roles"""
    # Verify document ownership
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    paragraphs = db.query(Paragraph).filter(
        Paragraph.document_id == document_id
    ).order_by(Paragraph.p_index).all()
    
    return paragraphs


@router.put("/paragraphs/{paragraph_id}", response_model=ParagraphResponse)
def update_paragraph(
    paragraph_id: UUID,
    paragraph_data: ParagraphUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update paragraph text, embedding, or structure"""
    paragraph = db.query(Paragraph).join(Document).filter(
        Paragraph.id == paragraph_id,
        Document.user_id == current_user.id
    ).first()
    
    if not paragraph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paragraph not found"
        )
    
    # Update fields
    if paragraph_data.text is not None:
        paragraph.text = paragraph_data.text
        paragraph.word_count = len(paragraph_data.text.split())
        import hashlib
        paragraph.hash = hashlib.md5(paragraph_data.text.encode()).hexdigest()
    if paragraph_data.emb is not None:
        paragraph.emb = paragraph_data.emb
    
    db.commit()
    db.refresh(paragraph)
    return paragraph


# Sentence endpoints
@router.get("/paragraphs/{paragraph_id}/sentences", response_model=List[SentenceResponse])
def get_paragraph_sentences(
    paragraph_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch sentences for paragraph-level analysis"""
    # Verify paragraph ownership through document
    paragraph = db.query(Paragraph).join(Document).filter(
        Paragraph.id == paragraph_id,
        Document.user_id == current_user.id
    ).first()
    
    if not paragraph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paragraph not found"
        )
    
    sentences = db.query(Sentence).filter(
        Sentence.paragraph_id == paragraph_id
    ).order_by(Sentence.s_index).all()
    
    return sentences
