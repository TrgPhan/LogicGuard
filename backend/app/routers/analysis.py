from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import Dict, Any, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.goal import Goal, RubricCriterion, WritingType
from app.models.analysis import AnalysisRun, AnalysisType, AnalysisStatus
from app.models.error import LogicError, ErrorType, ErrorCategory, Severity
from app.schemas.analysis import AnalysisRunCreate, AnalysisRunResponse, AnalysisResultResponse
from app.schemas.error import LogicErrorResponse

# Import AI analysis function with error handling
try:
    from app.ai.models.Analysis import analyze_document as ai_analyze_document
except ImportError as e:
    print(f"Warning: Could not import AI analysis function: {e}")
    # Create a dummy function for development/testing
    def ai_analyze_document(context, content, language="en"):
        return {
            "success": False,
            "metadata": {"error": "AI analysis module not available"}
        }

router = APIRouter()


def _build_analysis_context(goal: Goal, db: Session) -> Dict[str, Any]:
    """Build context dictionary for AI analysis from goal"""
    context = {
        "writing_type": "Document",
        "main_goal": "",
        "criteria": [],
        "constraints": []
    }
    
    if goal:
        # Get writing type
        if goal.writing_type:
            context["writing_type"] = goal.writing_type.display_name
        elif goal.writing_type_custom:
            context["writing_type"] = goal.writing_type_custom
        
        # Get main goal from rubric text (first line or summary)
        if goal.rubric_text:
            lines = [line.strip() for line in goal.rubric_text.split('\n') if line.strip()]
            if lines:
                context["main_goal"] = lines[0]
        
        # Get criteria from RubricCriterion
        criteria = db.query(RubricCriterion).filter(
            RubricCriterion.goal_id == goal.id
        ).order_by(RubricCriterion.order_index).all()
        
        context["criteria"] = [criterion.label for criterion in criteria]
        
        # Get constraints
        if goal.key_constraints:
            context["constraints"] = list(goal.key_constraints)
    
    return context


def _map_ai_result_to_logic_errors(
    ai_result: Dict[str, Any],
    analysis_run: AnalysisRun,
    document: Document,
    db: Session
) -> List[LogicError]:
    """Map AI analysis results to LogicError database records"""
    errors = []
    
    # Map contradictions
    contradictions = ai_result.get("contradictions", {}).get("items", [])
    for item in contradictions:
        error = LogicError(
            analysis_run_id=analysis_run.id,
            document_id=document.id,
            error_type=ErrorType.CONTRADICTION.value,  # Use .value to get "contradiction" string
            error_category=ErrorCategory.LOGIC.value,  # Use .value to get "logic" string
            severity=Severity.CRITICAL.value,  # Use .value to get "critical" string
            message=item.get("explanation", item.get("message", "Contradiction found")),
            meta={
                "text": item.get("text", ""),
                "contradicts_with": item.get("contradicts_with", ""),
                "suggestion": item.get("suggestion", "")
            }
        )
        errors.append(error)
    
    # Map undefined terms
    undefined_terms = ai_result.get("undefined_terms", {}).get("items", [])
    for item in undefined_terms:
        error = LogicError(
            analysis_run_id=analysis_run.id,
            document_id=document.id,
            error_type=ErrorType.UNDEFINED_TECHNICAL_TERM.value,  # Use .value
            error_category=ErrorCategory.CLARITY.value,  # Use .value
            severity=Severity.MEDIUM.value,  # Use .value
            message=item.get("explanation", item.get("message", "Undefined term found")),
            meta={
                "term": item.get("term", ""),
                "context": item.get("context", ""),
                "suggestion": item.get("suggestion", "")
            }
        )
        errors.append(error)
    
    # Map unsupported claims
    unsupported_claims = ai_result.get("unsupported_claims", {}).get("items", [])
    for item in unsupported_claims:
        error = LogicError(
            analysis_run_id=analysis_run.id,
            document_id=document.id,
            error_type=ErrorType.UNSUPPORTED_CLAIM.value,  # Use .value to get "unsupported_claim" string
            error_category=ErrorCategory.LOGIC.value,  # Use .value
            severity=Severity.MEDIUM.value,  # Use .value
            message=item.get("explanation", item.get("message", "Unsupported claim found")),
            meta={
                "claim": item.get("claim", ""),
                "evidence_quality": item.get("evidence_quality", ""),
                "suggestion": item.get("suggestion", "")
            }
        )
        errors.append(error)
    
    # Map logical jumps
    logical_jumps = ai_result.get("logical_jumps", {}).get("items", [])
    for item in logical_jumps:
        error = LogicError(
            analysis_run_id=analysis_run.id,
            document_id=document.id,
            error_type=ErrorType.LOGIC_GAP.value,  # Use .value
            error_category=ErrorCategory.LOGIC.value,  # Use .value
            severity=Severity.MEDIUM.value,  # Use .value
            message=item.get("explanation", item.get("message", "Logical jump found")),
            meta={
                "from": item.get("from", ""),
                "to": item.get("to", ""),
                "missing_step": item.get("missing_step", ""),
                "suggestion": item.get("suggestion", "")
            }
        )
        errors.append(error)
    
    return errors


@router.post("/documents/{document_id}/analyze", response_model=AnalysisRunResponse, status_code=status.HTTP_201_CREATED)
def analyze_document(
    document_id: UUID,
    analysis_data: AnalysisRunCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger analysis on a document using AI"""
    # Verify document belongs to user
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get goal if document has one
    goal = None
    if document.goal_id:
        goal = db.query(Goal).filter(Goal.id == document.goal_id).first()
    
    # Build context for AI analysis
    context = _build_analysis_context(goal, db)
    
    # Get document content
    content = document.content_full or ""
    
    if not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document content is empty"
        )
    
    # Create analysis run
    # Force string values to ensure SQLAlchemy doesn't convert to enum member name
    analysis_type_value = str(AnalysisType.FULL.value)  # Ensure it's a plain string "full"
    status_value = str(AnalysisStatus.RUNNING.value)  # Ensure it's a plain string "running"
    
    print(f"[Analysis] Creating analysis run with type='{analysis_type_value}', status='{status_value}'")
    
    analysis_run = AnalysisRun(
        document_id=document_id,
        doc_version=document.version,
        analysis_type=analysis_type_value,
        trigger_source=analysis_data.trigger_source,
        status=status_value,
        started_at=datetime.utcnow()
    )
    
    db.add(analysis_run)
    db.commit()
    db.refresh(analysis_run)
    
    try:
        # Call AI analysis (synchronous for now, can be made async later)
        # Detect language from content (simple heuristic: check for Vietnamese characters)
        language = "vi" if any(ord(char) >= 0x0100 for char in content[:500]) else "en"
        
        print(f"[Analysis] Starting AI analysis for document {document_id}, language: {language}")
        print(f"[Analysis] Context: {context}")
        print(f"[Analysis] Content length: {len(content)}")
        
        import time
        analysis_start = time.time()
        
        try:
            ai_result = ai_analyze_document(context, content, language=language)
            
            analysis_elapsed = time.time() - analysis_start
            print(f"[Analysis] AI analysis completed in {analysis_elapsed:.2f} seconds, success: {ai_result.get('success')}")
            
        except Exception as ai_error:
            analysis_elapsed = time.time() - analysis_start
            error_msg = f"AI analysis error after {analysis_elapsed:.2f} seconds: {str(ai_error)}"
            print(f"❌ [Analysis] {error_msg}")
            import traceback
            traceback.print_exc()
            
            analysis_run.status = AnalysisStatus.FAILED.value
            analysis_run.error_message = error_msg
            analysis_run.finished_at = datetime.utcnow()
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        if not ai_result.get("success"):
            error_msg = ai_result.get("metadata", {}).get("error", "Analysis failed")
            print(f"❌ [Analysis] Analysis failed: {error_msg}")
            analysis_run.status = AnalysisStatus.FAILED.value
            analysis_run.error_message = error_msg
            analysis_run.finished_at = datetime.utcnow()
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {error_msg}"
            )
        
        print(f"[Analysis] Processing {len(ai_result.get('contradictions', {}).get('items', []))} contradictions, {len(ai_result.get('undefined_terms', {}).get('items', []))} undefined terms, etc.")
        
        if not ai_result.get("success"):
            error_msg = ai_result.get("metadata", {}).get("error", "Analysis failed")
            analysis_run.status = AnalysisStatus.FAILED.value
            analysis_run.error_message = error_msg
            analysis_run.finished_at = datetime.utcnow()
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {error_msg}"
            )
        
        # Map AI results to LogicError records
        errors = _map_ai_result_to_logic_errors(ai_result, analysis_run, document, db)
        
        # Save errors to database
        try:
            for error in errors:
                db.add(error)
            
            # Update analysis run stats
            analysis_run.stats = {
                "total_issues": ai_result.get("summary", {}).get("total_issues", 0),
                "contradictions": ai_result.get("contradictions", {}).get("total_found", 0),
                "undefined_terms": ai_result.get("undefined_terms", {}).get("total_found", 0),
                "unsupported_claims": ai_result.get("unsupported_claims", {}).get("total_found", 0),
                "logical_jumps": ai_result.get("logical_jumps", {}).get("total_found", 0),
                "document_quality_score": ai_result.get("summary", {}).get("document_quality_score", 0)
            }
            
            analysis_run.status = AnalysisStatus.COMPLETED.value
            analysis_run.finished_at = datetime.utcnow()
            
            db.commit()
            db.refresh(analysis_run)
            
            print(f"[Analysis] Successfully saved {len(errors)} errors to database")
            
        except Exception as db_error:
            # Rollback on error
            db.rollback()
            print(f"❌ [Analysis] Database error when saving errors: {db_error}")
            import traceback
            traceback.print_exc()
            raise
        
    except HTTPException:
        raise
    except ImportError as e:
        # Mark analysis as failed
        analysis_run.status = AnalysisStatus.FAILED.value
        error_msg = f"Import error: {str(e)}. Please check AI models are properly installed."
        analysis_run.error_message = error_msg
        analysis_run.finished_at = datetime.utcnow()
        db.commit()
        print(f"[Analysis] Import error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    except Exception as e:
        # Mark analysis as failed
        analysis_run.status = AnalysisStatus.FAILED.value
        error_msg = str(e)
        analysis_run.error_message = error_msg
        analysis_run.finished_at = datetime.utcnow()
        db.commit()
        print(f"[Analysis] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis error: {error_msg}"
        )
    
    return analysis_run


@router.get("/documents/{document_id}/analysis/latest", response_model=AnalysisResultResponse)
def get_latest_analysis(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the latest analysis results for a document"""
    # Verify document belongs to user
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get latest completed analysis run
    analysis_run = db.query(AnalysisRun).filter(
        AnalysisRun.document_id == document_id,
        AnalysisRun.status == AnalysisStatus.COMPLETED.value
    ).order_by(AnalysisRun.created_at.desc()).first()
    
    if not analysis_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completed analysis found for this document"
        )
    
    # Get all errors from this analysis run
    errors = db.query(LogicError).filter(
        LogicError.analysis_run_id == analysis_run.id,
        LogicError.is_resolved == False
    ).all()
    
    return AnalysisResultResponse(
        analysis_run=analysis_run,
        errors=[LogicErrorResponse.model_validate(error) for error in errors],
        total_issues=len(errors)
    )
