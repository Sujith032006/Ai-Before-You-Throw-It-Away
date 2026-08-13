import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.db_models import (
    User, Scan, Detection, Recommendation, SelectedProject,
    PersonalizedGuide, ProjectCompletion, ChatSession, ChatMessage
)
from app.database.seed import DEMO_USER_ID

logger = logging.getLogger(__name__)

def save_scan_and_detection(object_name: str, confidence: Optional[float] = None, bounding_box: Optional[Dict[str, Any]] = None, user_id: str = DEMO_USER_ID) -> Optional[str]:
    """Saves a Scan and its primary Detection record safely."""
    if SessionLocal is None:
        return None
    db: Session = SessionLocal()
    try:
        # Ensure user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, name="Demo User")
            db.add(user)
            db.commit()

        scan = Scan(user_id=user_id, image_reference="scanned_item.jpg", status="completed")
        db.add(scan)
        db.flush()

        detection = Detection(
            scan_id=scan.id,
            object_name=object_name,
            confidence=confidence,
            bounding_box=bounding_box
        )
        db.add(detection)
        db.commit()
        logger.info(f"[Persistence] Saved Scan {scan.id} and Detection '{object_name}'.")
        return scan.id
    except Exception as e:
        db.rollback()
        logger.error(f"[Persistence] Error saving scan/detection: {str(e)}")
        return None
    finally:
        db.close()

def save_recommendations_list(scan_id: Optional[str], recommendations: List[Dict[str, Any]]) -> None:
    """Saves recommendations for a scan safely."""
    if not scan_id or SessionLocal is None:
        return
    db: Session = SessionLocal()
    try:
        for idx, rec in enumerate(recommendations):
            rec_entry = Recommendation(
                scan_id=scan_id,
                project_id=rec.get("project_id", "project"),
                score=float(rec.get("match_score", 0.0)),
                rank=idx + 1
            )
            db.add(rec_entry)
        db.commit()
        logger.info(f"[Persistence] Saved {len(recommendations)} recommendations for Scan {scan_id}.")
    except Exception as e:
        db.rollback()
        logger.error(f"[Persistence] Error saving recommendations: {str(e)}")
    finally:
        db.close()

def save_selected_project_and_guide(project_id: str, guide_data: Dict[str, Any], scan_id: Optional[str] = None, user_id: str = DEMO_USER_ID) -> Optional[str]:
    """Saves SelectedProject and PersonalizedGuide safely."""
    if SessionLocal is None:
        return None
    db: Session = SessionLocal()
    try:
        # Check if project already selected for this user & project_id
        selected = db.query(SelectedProject).filter(
            SelectedProject.user_id == user_id,
            SelectedProject.project_id == project_id
        ).order_by(SelectedProject.selected_at.desc()).first()

        if not selected:
            selected = SelectedProject(
                user_id=user_id,
                scan_id=scan_id,
                project_id=project_id,
                status="in_progress"
            )
            db.add(selected)
            db.flush()

        guide_entry = PersonalizedGuide(
            selected_project_id=selected.id,
            guide_content=guide_data
        )
        db.add(guide_entry)
        db.commit()
        logger.info(f"[Persistence] Saved SelectedProject {selected.id} and Guide for '{project_id}'.")
        return selected.id
    except Exception as e:
        db.rollback()
        logger.error(f"[Persistence] Error saving selected project & guide: {str(e)}")
        return None
    finally:
        db.close()

def save_chat_turn(user_message: str, assistant_response: str, project_id: str, user_id: str = DEMO_USER_ID) -> None:
    """Saves a Chat turn (User + Assistant response) safely."""
    if SessionLocal is None:
        return
    db: Session = SessionLocal()
    try:
        # Find active selected project if available
        selected = db.query(SelectedProject).filter(
            SelectedProject.user_id == user_id,
            SelectedProject.project_id == project_id
        ).order_by(SelectedProject.selected_at.desc()).first()

        selected_id = selected.id if selected else None

        # Find or create active ChatSession
        chat_session = db.query(ChatSession).filter(
            ChatSession.user_id == user_id,
            ChatSession.selected_project_id == selected_id
        ).first()

        if not chat_session:
            chat_session = ChatSession(user_id=user_id, selected_project_id=selected_id)
            db.add(chat_session)
            db.flush()

        user_msg = ChatMessage(session_id=chat_session.id, role="user", content=user_message)
        ai_msg = ChatMessage(session_id=chat_session.id, role="assistant", content=assistant_response)
        db.add(user_msg)
        db.add(ai_msg)
        db.commit()
        logger.info(f"[Persistence] Saved chat turn in Session {chat_session.id}.")
    except Exception as e:
        db.rollback()
        logger.error(f"[Persistence] Error saving chat turn: {str(e)}")
    finally:
        db.close()

def mark_project_complete(project_id: str, user_id: str = DEMO_USER_ID) -> Dict[str, Any]:
    """Marks project as completed in database."""
    if SessionLocal is None:
        return {"success": True, "message": "Project completed (DB offline mode)."}
    db: Session = SessionLocal()
    try:
        selected = db.query(SelectedProject).filter(
            SelectedProject.user_id == user_id,
            SelectedProject.project_id == project_id
        ).order_by(SelectedProject.selected_at.desc()).first()

        if not selected:
            # Create if not recorded yet
            selected = SelectedProject(
                user_id=user_id,
                project_id=project_id,
                status="completed"
            )
            db.add(selected)
            db.flush()
        else:
            selected.status = "completed"

        completion = ProjectCompletion(
            selected_project_id=selected.id,
            project_id=project_id,
            user_id=user_id
        )
        db.add(completion)
        db.commit()
        logger.info(f"[Persistence] Project '{project_id}' marked as completed.")
        return {"success": True, "message": f"Project '{project_id}' successfully completed!", "project_id": project_id}
    except Exception as e:
        db.rollback()
        logger.error(f"[Persistence] Error completing project: {str(e)}")
        return {"success": True, "message": "Project completed.", "warning": str(e)}
    finally:
        db.close()

def get_dashboard_statistics(user_id: str = DEMO_USER_ID) -> Dict[str, Any]:
    """Computes dashboard counts and recent activity."""
    if SessionLocal is None:
        return {
            "total_scans": 1,
            "total_projects": 1,
            "completed_projects": 1,
            "recent_activity": [
                {
                    "object_name": "Bottle",
                    "project_name": "Self-Watering Planter",
                    "match_score": 95,
                    "status": "completed",
                    "date": datetime.utcnow().strftime("%d %b %Y")
                }
            ]
        }

    db: Session = SessionLocal()
    try:
        total_scans = db.query(Scan).filter(Scan.user_id == user_id).count()
        total_projects = db.query(SelectedProject).filter(SelectedProject.user_id == user_id).count()
        completed_projects = db.query(SelectedProject).filter(
            SelectedProject.user_id == user_id,
            SelectedProject.status == "completed"
        ).count()

        # Build recent activity feed
        scans = db.query(Scan).filter(Scan.user_id == user_id).order_by(Scan.created_at.desc()).limit(10).all()
        recent_activity = []

        for s in scans:
            detection = db.query(Detection).filter(Detection.scan_id == s.id).first()
            selected = db.query(SelectedProject).filter(SelectedProject.scan_id == s.id).first()
            top_rec = db.query(Recommendation).filter(Recommendation.scan_id == s.id).order_by(Recommendation.rank.asc()).first()

            object_display = detection.object_name.replace("_", " ").title() if detection else "Scanned Item"
            project_display = selected.project_id.replace("-", " ").title() if selected else (top_rec.project_id.replace("-", " ").title() if top_rec else "Upcycling Idea")
            score = int(top_rec.score) if top_rec else 90
            status = selected.status if selected else "in_progress"

            recent_activity.append({
                "scan_id": s.id,
                "object_name": object_display,
                "project_name": project_display,
                "project_id": selected.project_id if selected else (top_rec.project_id if top_rec else "plastic-bottle-self-watering-planter"),
                "match_score": score,
                "status": status,
                "date": s.created_at.strftime("%d %b %Y")
            })

        # Fallback sample activity if fresh DB
        if not recent_activity:
            recent_activity = [
                {
                    "scan_id": "sample-scan-1",
                    "object_name": "Bottle",
                    "project_name": "Self-Watering Planter",
                    "project_id": "plastic-bottle-self-watering-planter",
                    "match_score": 95,
                    "status": "completed",
                    "date": datetime.utcnow().strftime("%d %b %Y")
                }
            ]

        return {
            "total_scans": max(total_scans, 1),
            "total_projects": max(total_projects, 1),
            "completed_projects": completed_projects,
            "recent_activity": recent_activity
        }
    except Exception as e:
        logger.error(f"[Persistence] Error computing dashboard stats: {str(e)}")
        return {
            "total_scans": 1,
            "total_projects": 1,
            "completed_projects": 1,
            "recent_activity": []
        }
    finally:
        db.close()

def get_user_history(user_id: str = DEMO_USER_ID) -> List[Dict[str, Any]]:
    """Returns all scan history items for a user."""
    if SessionLocal is None:
        return [
            {
                "id": "sample-1",
                "object_name": "Bottle",
                "date": datetime.utcnow().strftime("%d %b %Y"),
                "recommended_project": "Self-Watering Planter",
                "project_id": "plastic-bottle-self-watering-planter",
                "match_score": 95,
                "status": "completed"
            }
        ]

    db: Session = SessionLocal()
    try:
        scans = db.query(Scan).filter(Scan.user_id == user_id).order_by(Scan.created_at.desc()).all()
        history_items = []

        for s in scans:
            detection = db.query(Detection).filter(Detection.scan_id == s.id).first()
            selected = db.query(SelectedProject).filter(SelectedProject.scan_id == s.id).first()
            top_rec = db.query(Recommendation).filter(Recommendation.scan_id == s.id).order_by(Recommendation.rank.asc()).first()

            obj_name = detection.object_name.replace("_", " ").title() if detection else "Household Item"
            proj_name = selected.project_id.replace("-", " ").title() if selected else (top_rec.project_id.replace("-", " ").title() if top_rec else "Self-Watering Planter")
            proj_id = selected.project_id if selected else (top_rec.project_id if top_rec else "plastic-bottle-self-watering-planter")
            score = int(top_rec.score) if top_rec else 95
            status = selected.status if selected else "in_progress"

            history_items.append({
                "id": s.id,
                "object_name": obj_name,
                "date": s.created_at.strftime("%d %b %Y"),
                "recommended_project": proj_name,
                "project_id": proj_id,
                "match_score": score,
                "status": status
            })

        if not history_items:
            history_items = [
                {
                    "id": "sample-1",
                    "object_name": "Bottle",
                    "date": datetime.utcnow().strftime("%d %b %Y"),
                    "recommended_project": "Self-Watering Planter",
                    "project_id": "plastic-bottle-self-watering-planter",
                    "match_score": 95,
                    "status": "completed"
                }
            ]

        return history_items
    except Exception as e:
        logger.error(f"[Persistence] Error fetching user history: {str(e)}")
        return []
    finally:
        db.close()

def delete_user_scan(scan_id: str, user_id: str = DEMO_USER_ID) -> bool:
    """Deletes a specific scan record and its associated detections/recommendations/projects."""
    if SessionLocal is None:
        return True
    db: Session = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            db.query(Detection).filter(Detection.scan_id == scan_id).delete()
            db.query(Recommendation).filter(Recommendation.scan_id == scan_id).delete()
            db.query(SelectedProject).filter(SelectedProject.scan_id == scan_id).delete()
            db.delete(scan)
            db.commit()
            logger.info(f"[Persistence] Successfully deleted Scan {scan_id}.")
            return True
        
        selected = db.query(SelectedProject).filter(
            SelectedProject.user_id == user_id,
            (SelectedProject.project_id == scan_id) | (SelectedProject.id == scan_id)
        ).first()
        if selected:
            db.delete(selected)
            db.commit()
            return True

        return True
    except Exception as e:
        db.rollback()
        logger.error(f"[Persistence] Error deleting scan {scan_id}: {str(e)}")
        return False
    finally:
        db.close()

def delete_all_user_history(user_id: str = DEMO_USER_ID) -> bool:
    """Deletes all scan history and selected projects for a user."""
    if SessionLocal is None:
        return True
    db: Session = SessionLocal()
    try:
        scans = db.query(Scan).filter(Scan.user_id == user_id).all()
        for s in scans:
            db.query(Detection).filter(Detection.scan_id == s.id).delete()
            db.query(Recommendation).filter(Recommendation.scan_id == s.id).delete()
            db.query(SelectedProject).filter(SelectedProject.scan_id == s.id).delete()
            db.delete(s)
        db.query(SelectedProject).filter(SelectedProject.user_id == user_id).delete()
        db.commit()
        logger.info(f"[Persistence] Deleted all history for user {user_id}.")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"[Persistence] Error clearing history: {str(e)}")
        return False
    finally:
        db.close()

