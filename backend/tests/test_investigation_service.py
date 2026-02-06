"""
Tests for Investigation Services
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.investigation import InvestigationService
from app.domain.user import User


class TestInvestigationService:
    """Test investigation service methods"""
    
    @pytest.fixture
    def investigation_service(self):
        """Create investigation service instance"""
        return InvestigationService()
    
    def test_create_investigation(
        self, 
        db: Session, 
        test_user: User, 
        mock_investigation_data: dict,
        investigation_service: InvestigationService
    ):
        """Test creating an investigation"""
        investigation = investigation_service.create_investigation(
            db=db,
            user_id=test_user.id,
            **mock_investigation_data
        )
        
        assert investigation.id is not None
        assert investigation.name == mock_investigation_data["name"]
        assert investigation.type == mock_investigation_data["type"]
        assert investigation.user_id == test_user.id
        assert investigation.status == "draft"
    
    def test_get_investigation(
        self,
        db: Session,
        test_user: User,
        mock_investigation_data: dict,
        investigation_service: InvestigationService
    ):
        """Test retrieving an investigation"""
        created = investigation_service.create_investigation(
            db=db,
            user_id=test_user.id,
            **mock_investigation_data
        )
        
        retrieved = investigation_service.get_investigation(
            db=db,
            investigation_id=created.id
        )
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name
    
    def test_get_nonexistent_investigation(
        self,
        db: Session,
        investigation_service: InvestigationService
    ):
        """Test retrieving nonexistent investigation"""
        result = investigation_service.get_investigation(
            db=db,
            investigation_id=99999
        )
        assert result is None
    
    def test_list_investigations(
        self,
        db: Session,
        test_user: User,
        investigation_service: InvestigationService
    ):
        """Test listing investigations"""
        # Create multiple investigations
        for i in range(3):
            investigation_service.create_investigation(
                db=db,
                user_id=test_user.id,
                name=f"Investigation {i}",
                type="property",
                description=f"Description {i}",
                target_document=f"12.345.678/000{i}-90"
            )
        
        investigations = investigation_service.list_investigations(
            db=db,
            user_id=test_user.id
        )
        
        assert len(investigations) == 3
        assert all(inv.user_id == test_user.id for inv in investigations)
    
    def test_update_investigation(
        self,
        db: Session,
        test_user: User,
        mock_investigation_data: dict,
        investigation_service: InvestigationService
    ):
        """Test updating an investigation"""
        investigation = investigation_service.create_investigation(
            db=db,
            user_id=test_user.id,
            **mock_investigation_data
        )
        
        updated = investigation_service.update_investigation(
            db=db,
            investigation_id=investigation.id,
            name="Updated Name",
            status="active"
        )
        
        assert updated.name == "Updated Name"
        assert updated.status == "active"
    
    def test_delete_investigation(
        self,
        db: Session,
        test_user: User,
        mock_investigation_data: dict,
        investigation_service: InvestigationService
    ):
        """Test deleting an investigation"""
        investigation = investigation_service.create_investigation(
            db=db,
            user_id=test_user.id,
            **mock_investigation_data
        )
        
        result = investigation_service.delete_investigation(
            db=db,
            investigation_id=investigation.id
        )
        
        assert result is True
        
        # Verify it's deleted
        deleted = investigation_service.get_investigation(
            db=db,
            investigation_id=investigation.id
        )
        assert deleted is None
    
    def test_filter_by_status(
        self,
        db: Session,
        test_user: User,
        investigation_service: InvestigationService
    ):
        """Test filtering investigations by status"""
        # Create investigations with different statuses
        statuses = ["draft", "active", "completed"]
        for status in statuses:
            investigation_service.create_investigation(
                db=db,
                user_id=test_user.id,
                name=f"Investigation {status}",
                type="property",
                description="Test",
                target_document="12.345.678/0001-90",
                status=status
            )
        
        active_investigations = investigation_service.list_investigations(
            db=db,
            user_id=test_user.id,
            status="active"
        )
        
        assert len(active_investigations) == 1
        assert active_investigations[0].status == "active"
    
    def test_pagination(
        self,
        db: Session,
        test_user: User,
        investigation_service: InvestigationService
    ):
        """Test investigation pagination"""
        # Create 10 investigations
        for i in range(10):
            investigation_service.create_investigation(
                db=db,
                user_id=test_user.id,
                name=f"Investigation {i}",
                type="property",
                description="Test",
                target_document=f"12.345.678/000{i}-90"
            )
        
        # Get first page (5 items)
        page1 = investigation_service.list_investigations(
            db=db,
            user_id=test_user.id,
            skip=0,
            limit=5
        )
        
        # Get second page
        page2 = investigation_service.list_investigations(
            db=db,
            user_id=test_user.id,
            skip=5,
            limit=5
        )
        
        assert len(page1) == 5
        assert len(page2) == 5
        assert page1[0].id != page2[0].id
    
    def test_search_investigations(
        self,
        db: Session,
        test_user: User,
        investigation_service: InvestigationService
    ):
        """Test searching investigations"""
        investigation_service.create_investigation(
            db=db,
            user_id=test_user.id,
            name="Fazenda São João",
            type="property",
            description="Rural property",
            target_document="12.345.678/0001-90"
        )
        
        investigation_service.create_investigation(
            db=db,
            user_id=test_user.id,
            name="Empresa XYZ Ltda",
            type="company",
            description="Company investigation",
            target_document="98.765.432/0001-10"
        )
        
        results = investigation_service.search_investigations(
            db=db,
            user_id=test_user.id,
            query="Fazenda"
        )
        
        assert len(results) == 1
        assert "Fazenda" in results[0].name
    
    def test_calculate_progress(
        self,
        db: Session,
        test_user: User,
        mock_investigation_data: dict,
        investigation_service: InvestigationService
    ):
        """Test progress calculation"""
        investigation = investigation_service.create_investigation(
            db=db,
            user_id=test_user.id,
            **mock_investigation_data
        )
        
        progress = investigation_service.calculate_progress(
            db=db,
            investigation_id=investigation.id
        )
        
        assert isinstance(progress, float)
        assert 0 <= progress <= 100
    
    def test_generate_report(
        self,
        db: Session,
        test_user: User,
        mock_investigation_data: dict,
        investigation_service: InvestigationService
    ):
        """Test report generation"""
        investigation = investigation_service.create_investigation(
            db=db,
            user_id=test_user.id,
            **mock_investigation_data
        )
        
        report = investigation_service.generate_report(
            db=db,
            investigation_id=investigation.id
        )
        
        assert report is not None
        assert "id" in report
        assert "name" in report
        assert "summary" in report


class TestInvestigationValidation:
    """Test investigation validation"""
    
    @pytest.fixture
    def investigation_service(self):
        return InvestigationService()
    
    def test_invalid_type(
        self,
        db: Session,
        test_user: User,
        investigation_service: InvestigationService
    ):
        """Test creating investigation with invalid type"""
        with pytest.raises(ValueError):
            investigation_service.create_investigation(
                db=db,
                user_id=test_user.id,
                name="Test",
                type="invalid_type",
                description="Test",
                target_document="12.345.678/0001-90"
            )
    
    def test_missing_required_fields(
        self,
        db: Session,
        test_user: User,
        investigation_service: InvestigationService
    ):
        """Test creating investigation without required fields"""
        with pytest.raises(ValueError):
            investigation_service.create_investigation(
                db=db,
                user_id=test_user.id,
                name="",  # Empty name
                type="property",
                description="Test",
                target_document="12.345.678/0001-90"
            )
    
    def test_invalid_document_format(
        self,
        db: Session,
        test_user: User,
        investigation_service: InvestigationService
    ):
        """Test creating investigation with invalid document format"""
        with pytest.raises(ValueError):
            investigation_service.create_investigation(
                db=db,
                user_id=test_user.id,
                name="Test",
                type="company",
                description="Test",
                target_document="invalid-document"
            )
