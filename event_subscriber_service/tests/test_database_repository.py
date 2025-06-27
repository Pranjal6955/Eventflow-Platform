import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from app.infrastructure.postgresql_repository import PostgreSQLRepository

class TestPostgreSQLRepository:
    
    @pytest.fixture
    def mock_session(self):
        session = Mock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        return session
    
    @pytest.fixture
    def mock_session_factory(self, mock_session):
        factory = Mock()
        factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        factory.return_value.__aexit__ = AsyncMock(return_value=None)
        return factory
    
    @pytest.mark.asyncio
    @patch('app.infrastructure.postgresql_repository.create_async_engine')
    @patch('app.infrastructure.postgresql_repository.async_sessionmaker')
    async def test_save_user_analytics_event_success(
        self, 
        mock_sessionmaker, 
        mock_engine,
        mock_session_factory,
        mock_session
    ):
        # Arrange
        mock_sessionmaker.return_value = mock_session_factory
        repo = PostgreSQLRepository()
        repo.async_session_factory = mock_session_factory
        
        mock_event = Mock()
        mock_event.id = uuid4()
        mock_session.add.side_effect = lambda event: setattr(event, 'id', mock_event.id)
        
        event_data = {
            "user_id": "test_user",
            "event_type": "click",
            "timestamp": "2024-01-01T12:00:00Z",
            "metadata": {"key": "value"}
        }
        
        # Act
        with patch('app.infrastructure.postgresql_repository.UserAnalyticsEvent') as MockEvent:
            MockEvent.return_value = mock_event
            result = await repo.save_user_analytics_event(event_data)
        
        # Assert
        assert result == mock_event.id
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.infrastructure.postgresql_repository.create_async_engine')
    @patch('app.infrastructure.postgresql_repository.async_sessionmaker')
    async def test_save_user_analytics_event_error(
        self, 
        mock_sessionmaker, 
        mock_engine,
        mock_session_factory,
        mock_session
    ):
        # Arrange
        mock_sessionmaker.return_value = mock_session_factory
        repo = PostgreSQLRepository()
        repo.async_session_factory = mock_session_factory
        
        mock_session.commit.side_effect = Exception("Database error")
        
        event_data = {
            "user_id": "test_user",
            "event_type": "click",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        # Act & Assert
        with patch('app.infrastructure.postgresql_repository.UserAnalyticsEvent'):
            with pytest.raises(Exception, match="Database error"):
                await repo.save_user_analytics_event(event_data)
        
        mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.infrastructure.postgresql_repository.create_async_engine')
    @patch('app.infrastructure.postgresql_repository.async_sessionmaker')
    async def test_get_user_analytics_events(
        self, 
        mock_sessionmaker, 
        mock_engine,
        mock_session_factory,
        mock_session
    ):
        # Arrange
        mock_sessionmaker.return_value = mock_session_factory
        repo = PostgreSQLRepository()
        repo.async_session_factory = mock_session_factory
        
        # Mock query result
        mock_events = [Mock(), Mock()]
        for i, event in enumerate(mock_events):
            event.id = uuid4()
            event.user_id = "test_user"
            event.event_type = f"event_{i}"
            event.timestamp = Mock()
            event.timestamp.isoformat.return_value = "2024-01-01T12:00:00Z"
            event.metadata = {"key": f"value_{i}"}
            event.processed_at = Mock()
            event.processed_at.isoformat.return_value = "2024-01-01T12:01:00Z"
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_events
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await repo.get_user_analytics_events("test_user", 10)
        
        # Assert
        assert len(result) == 2
        assert result[0]["user_id"] == "test_user"
        assert result[0]["event_type"] == "event_0"
