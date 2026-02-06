"""
Testes do Sistema de Colaboração
Testa compartilhamento, comentários e histórico
"""
import pytest
from datetime import datetime, timedelta
from app.services.collaboration import (
    collaboration_service,
    PermissionLevel,
    InvestigationShare,
    InvestigationComment,
    InvestigationChangeLog
)


# ==================== Testes de Compartilhamento ====================

@pytest.mark.asyncio
async def test_share_investigation(db_session, test_user, test_user2, test_investigation):
    """Teste: Compartilhar investigação"""
    share = await collaboration_service.share_investigation(
        db_session,
        investigation_id=test_investigation.id,
        owner_id=test_user.id,
        shared_with_email=test_user2.email,
        permission=PermissionLevel.EDIT
    )
    
    assert share is not None
    assert share.investigation_id == test_investigation.id
    assert share.owner_id == test_user.id
    assert share.shared_with_id == test_user2.id
    assert share.permission == PermissionLevel.EDIT.value
    assert share.is_active is True


@pytest.mark.asyncio
async def test_share_with_expiration(db_session, test_user, test_user2, test_investigation):
    """Teste: Compartilhar com data de expiração"""
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    share = await collaboration_service.share_investigation(
        db_session,
        investigation_id=test_investigation.id,
        owner_id=test_user.id,
        shared_with_email=test_user2.email,
        permission=PermissionLevel.VIEW,
        expires_at=expires_at
    )
    
    assert share.expires_at is not None
    assert share.expires_at == expires_at


@pytest.mark.asyncio
async def test_share_nonexistent_user(db_session, test_user, test_investigation):
    """Teste: Tentar compartilhar com usuário inexistente"""
    with pytest.raises(ValueError, match="não encontrado"):
        await collaboration_service.share_investigation(
            db_session,
            investigation_id=test_investigation.id,
            owner_id=test_user.id,
            shared_with_email="naoexiste@example.com",
            permission=PermissionLevel.VIEW
        )


@pytest.mark.asyncio
async def test_update_existing_share(db_session, test_user, test_user2, test_investigation):
    """Teste: Atualizar compartilhamento existente"""
    # Compartilhar com VIEW
    share1 = await collaboration_service.share_investigation(
        db_session,
        investigation_id=test_investigation.id,
        owner_id=test_user.id,
        shared_with_email=test_user2.email,
        permission=PermissionLevel.VIEW
    )
    
    assert share1.permission == PermissionLevel.VIEW.value
    
    # Atualizar para EDIT
    share2 = await collaboration_service.share_investigation(
        db_session,
        investigation_id=test_investigation.id,
        owner_id=test_user.id,
        shared_with_email=test_user2.email,
        permission=PermissionLevel.EDIT
    )
    
    assert share2.id == share1.id  # Mesmo compartilhamento
    assert share2.permission == PermissionLevel.EDIT.value


@pytest.mark.asyncio
async def test_revoke_access(db_session, test_user, test_user2, test_investigation):
    """Teste: Remover acesso de usuário"""
    # Compartilhar
    share = await collaboration_service.share_investigation(
        db_session,
        investigation_id=test_investigation.id,
        owner_id=test_user.id,
        shared_with_email=test_user2.email,
        permission=PermissionLevel.VIEW
    )
    
    assert share.is_active is True
    
    # Remover acesso
    success = await collaboration_service.revoke_access(
        db_session,
        investigation_id=test_investigation.id,
        owner_id=test_user.id,
        shared_with_id=test_user2.id
    )
    
    assert success is True
    
    # Verificar que foi desativado
    await db_session.refresh(share)
    assert share.is_active is False


# ==================== Testes de Permissões ====================

@pytest.mark.asyncio
async def test_check_permission_owner(db_session, test_user, test_investigation):
    """Teste: Dono tem todas as permissões"""
    has_view = await collaboration_service.check_permission(
        db_session,
        test_investigation.id,
        test_user.id,
        PermissionLevel.VIEW
    )
    
    has_admin = await collaboration_service.check_permission(
        db_session,
        test_investigation.id,
        test_user.id,
        PermissionLevel.ADMIN
    )
    
    assert has_view is True
    assert has_admin is True


@pytest.mark.asyncio
async def test_check_permission_shared_user(db_session, test_user, test_user2, test_investigation):
    """Teste: Usuário compartilhado tem permissões corretas"""
    # Compartilhar com COMMENT
    await collaboration_service.share_investigation(
        db_session,
        investigation_id=test_investigation.id,
        owner_id=test_user.id,
        shared_with_email=test_user2.email,
        permission=PermissionLevel.COMMENT
    )
    
    # Deve ter VIEW
    has_view = await collaboration_service.check_permission(
        db_session,
        test_investigation.id,
        test_user2.id,
        PermissionLevel.VIEW
    )
    assert has_view is True
    
    # Deve ter COMMENT
    has_comment = await collaboration_service.check_permission(
        db_session,
        test_investigation.id,
        test_user2.id,
        PermissionLevel.COMMENT
    )
    assert has_comment is True
    
    # Não deve ter ADMIN
    has_admin = await collaboration_service.check_permission(
        db_session,
        test_investigation.id,
        test_user2.id,
        PermissionLevel.ADMIN
    )
    assert has_admin is False


@pytest.mark.asyncio
async def test_check_permission_hierarchy(db_session, test_user, test_user2, test_investigation):
    """Teste: Hierarquia de permissões"""
    # Compartilhar com EDIT
    await collaboration_service.share_investigation(
        db_session,
        investigation_id=test_investigation.id,
        owner_id=test_user.id,
        shared_with_email=test_user2.email,
        permission=PermissionLevel.EDIT
    )
    
    # EDIT deve dar acesso a VIEW e COMMENT também
    assert await collaboration_service.check_permission(
        db_session, test_investigation.id, test_user2.id, PermissionLevel.VIEW
    ) is True
    
    assert await collaboration_service.check_permission(
        db_session, test_investigation.id, test_user2.id, PermissionLevel.COMMENT
    ) is True
    
    assert await collaboration_service.check_permission(
        db_session, test_investigation.id, test_user2.id, PermissionLevel.EDIT
    ) is True


@pytest.mark.asyncio
async def test_check_permission_expired_share(db_session, test_user, test_user2, test_investigation):
    """Teste: Compartilhamento expirado não dá acesso"""
    # Compartilhar com expiração no passado
    expired_date = datetime.utcnow() - timedelta(days=1)
    
    await collaboration_service.share_investigation(
        db_session,
        investigation_id=test_investigation.id,
        owner_id=test_user.id,
        shared_with_email=test_user2.email,
        permission=PermissionLevel.VIEW,
        expires_at=expired_date
    )
    
    # Não deve ter acesso
    has_permission = await collaboration_service.check_permission(
        db_session,
        test_investigation.id,
        test_user2.id,
        PermissionLevel.VIEW
    )
    
    assert has_permission is False


# ==================== Testes de Comentários ====================

@pytest.mark.asyncio
async def test_add_comment(db_session, test_user, test_investigation):
    """Teste: Adicionar comentário"""
    comment = await collaboration_service.add_comment(
        db_session,
        investigation_id=test_investigation.id,
        user_id=test_user.id,
        content="Este é um comentário de teste"
    )
    
    assert comment is not None
    assert comment.investigation_id == test_investigation.id
    assert comment.user_id == test_user.id
    assert comment.content == "Este é um comentário de teste"
    assert comment.is_internal is False
    assert comment.is_deleted is False


@pytest.mark.asyncio
async def test_add_internal_comment(db_session, test_user, test_investigation):
    """Teste: Adicionar anotação privada"""
    comment = await collaboration_service.add_comment(
        db_session,
        investigation_id=test_investigation.id,
        user_id=test_user.id,
        content="Anotação privada",
        is_internal=True
    )
    
    assert comment.is_internal is True


@pytest.mark.asyncio
async def test_add_reply_comment(db_session, test_user, test_investigation):
    """Teste: Adicionar resposta a comentário"""
    # Comentário pai
    parent_comment = await collaboration_service.add_comment(
        db_session,
        investigation_id=test_investigation.id,
        user_id=test_user.id,
        content="Comentário pai"
    )
    
    # Resposta
    reply = await collaboration_service.add_comment(
        db_session,
        investigation_id=test_investigation.id,
        user_id=test_user.id,
        content="Resposta ao comentário",
        parent_id=parent_comment.id
    )
    
    assert reply.parent_id == parent_comment.id


# ==================== Testes de Histórico ====================

@pytest.mark.asyncio
async def test_log_change(db_session, test_user, test_investigation):
    """Teste: Registrar alteração no histórico"""
    log = await collaboration_service.log_change(
        db_session,
        investigation_id=test_investigation.id,
        user_id=test_user.id,
        action="updated",
        field_changed="status",
        old_value={"status": "pending"},
        new_value={"status": "completed"},
        description="Status alterado de pending para completed"
    )
    
    assert log is not None
    assert log.investigation_id == test_investigation.id
    assert log.user_id == test_user.id
    assert log.action == "updated"
    assert log.field_changed == "status"
    assert log.old_value == {"status": "pending"}
    assert log.new_value == {"status": "completed"}


@pytest.mark.asyncio
async def test_get_shared_investigations(db_session, test_user, test_user2, test_investigation):
    """Teste: Buscar investigações compartilhadas"""
    # Compartilhar
    await collaboration_service.share_investigation(
        db_session,
        investigation_id=test_investigation.id,
        owner_id=test_user.id,
        shared_with_email=test_user2.email,
        permission=PermissionLevel.VIEW
    )
    
    # Buscar investigações compartilhadas com test_user2
    shared = await collaboration_service.get_shared_investigations(
        db_session,
        user_id=test_user2.id,
        include_owned=False
    )
    
    assert len(shared) > 0
    assert any(inv['id'] == test_investigation.id for inv in shared)


# ==================== Contagem de Testes ====================

def test_count():
    """Verifica quantidade de testes"""
    import inspect
    import sys
    
    module = sys.modules[__name__]
    test_functions = [name for name, obj in inspect.getmembers(module)
                     if inspect.isfunction(obj) and name.startswith('test_')]
    
    print(f"\n✅ Total de testes de colaboração: {len(test_functions)}")
    assert len(test_functions) >= 15  # Pelo menos 15 testes


# Fixtures necessárias (devem estar em conftest.py)
"""
@pytest.fixture
async def test_user(db_session):
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def test_user2(db_session):
    user = User(
        email="test2@example.com",
        full_name="Test User 2",
        hashed_password="hashed"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def test_investigation(db_session, test_user):
    investigation = Investigation(
        user_id=test_user.id,
        target_name="Test Target",
        target_cpf_cnpj="123.456.789-00",
        status="pending"
    )
    db_session.add(investigation)
    await db_session.commit()
    await db_session.refresh(investigation)
    return investigation
"""
