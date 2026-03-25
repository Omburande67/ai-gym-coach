"""Unit tests for WebSocket endpoint and WorkoutSession."""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from app.main import app
from app.api.websocket import WorkoutSession, WebSocketManager
from app.models.pose import PoseData, PoseKeypoint
from app.models.exercise import ExerciseType


@pytest.fixture
def sample_pose_data():
    """Create sample pose data for testing."""
    keypoints = []
    joint_names = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle",
        "left_heel", "right_heel", "left_foot_index", "right_foot_index",
        "left_pinky", "right_pinky", "left_index", "right_index",
        "left_thumb", "right_thumb", "left_hip_center", "right_hip_center",
        "left_shoulder_center", "right_shoulder_center", "spine_mid", "spine_base"
    ]
    
    for name in joint_names:
        keypoints.append(PoseKeypoint(
            x=0.5,
            y=0.5,
            z=0.0,
            visibility=0.9,
            name=name
        ))
    
    return PoseData(
        keypoints=keypoints,
        timestamp=1234567890.0
    )


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection."""
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    websocket.send_json = AsyncMock()
    websocket.receive_text = AsyncMock()
    return websocket


class TestWorkoutSession:
    """Test WorkoutSession class."""
    
    @pytest.mark.asyncio
    async def test_session_initialization(self, mock_websocket):
        """Test that WorkoutSession initializes correctly."""
        session = WorkoutSession("user123", mock_websocket)
        
        assert session.user_id == "user123"
        assert session.websocket == mock_websocket
        assert session.exercise_recognizer is not None
        assert session.rep_counter is None
        assert session.form_analyzer is not None
        assert session.current_exercise is None
        assert session.is_active is True
    
    @pytest.mark.asyncio
    async def test_send_feedback(self, mock_websocket):
        """Test sending feedback through WebSocket."""
        session = WorkoutSession("user123", mock_websocket)
        
        feedback = {"type": "test", "data": "value"}
        await session.send_feedback(feedback)
        
        mock_websocket.send_json.assert_called_once_with(feedback)
    
    @pytest.mark.asyncio
    async def test_send_feedback_error_handling(self, mock_websocket):
        """Test that send_feedback handles errors gracefully."""
        session = WorkoutSession("user123", mock_websocket)
        mock_websocket.send_json.side_effect = Exception("Connection error")
        
        # Should not raise exception
        await session.send_feedback({"type": "test"})
        
        # Session should be marked as inactive
        assert session.is_active is False
    
    @pytest.mark.asyncio
    async def test_handle_pose_data_exercise_detection(self, mock_websocket, sample_pose_data):
        """Test that pose data triggers exercise detection."""
        session = WorkoutSession("user123", mock_websocket)
        
        # Mock exercise recognizer to return a specific exercise
        with patch.object(session.exercise_recognizer, 'recognize', return_value=(ExerciseType.PUSHUP, 0.95)):
            await session.handle_pose_data(sample_pose_data)
        
        # Should send exercise_detected message
        assert mock_websocket.send_json.called
        call_args = mock_websocket.send_json.call_args_list[0][0][0]
        assert call_args["type"] == "exercise_detected"
        assert call_args["exercise"] == "pushup"
        assert call_args["confidence"] == 0.95
        
        # Should create rep counter
        assert session.rep_counter is not None
        assert session.current_exercise == ExerciseType.PUSHUP
    
    @pytest.mark.asyncio
    async def test_handle_pose_data_rep_counting(self, mock_websocket, sample_pose_data):
        """Test that pose data triggers rep counting."""
        session = WorkoutSession("user123", mock_websocket)
        session.current_exercise = ExerciseType.PUSHUP
        
        # Create mock rep counter
        mock_rep_counter = Mock()
        mock_rep_counter.update.return_value = 5  # Rep completed
        session.rep_counter = mock_rep_counter
        
        # Mock exercise recognizer to return same exercise
        with patch.object(session.exercise_recognizer, 'recognize', return_value=(ExerciseType.PUSHUP, 0.95)):
            await session.handle_pose_data(sample_pose_data)
        
        # Should call rep counter update
        mock_rep_counter.update.assert_called_once_with(sample_pose_data)
        
        # Should send rep_counted message
        rep_messages = [call[0][0] for call in mock_websocket.send_json.call_args_list 
                       if call[0][0].get("type") == "rep_counted"]
        assert len(rep_messages) > 0
        assert rep_messages[0]["count"] == 5
        assert rep_messages[0]["total"] == 5
    
    @pytest.mark.asyncio
    async def test_handle_pose_data_form_analysis(self, mock_websocket, sample_pose_data):
        """Test that pose data triggers form analysis."""
        session = WorkoutSession("user123", mock_websocket)
        session.current_exercise = ExerciseType.PUSHUP
        
        # Mock form analyzer to return mistakes
        from app.models.exercise import FormMistake
        mock_mistakes = [
            FormMistake(
                mistake_type="hip_sag",
                severity=0.6,
                suggestion="Engage your core"
            )
        ]
        
        with patch.object(session.form_analyzer, 'analyze', return_value=mock_mistakes):
            with patch.object(session.form_analyzer, 'calculate_form_score', return_value=85.0):
                with patch.object(session.exercise_recognizer, 'recognize', 
                                return_value=(ExerciseType.PUSHUP, 0.95)):
                    await session.handle_pose_data(sample_pose_data)
        
        # Should send form_feedback message
        form_messages = [call[0][0] for call in mock_websocket.send_json.call_args_list 
                        if call[0][0].get("type") == "form_feedback"]
        assert len(form_messages) > 0
        assert form_messages[0]["form_score"] == 85.0
        assert len(form_messages[0]["mistakes"]) == 1
        assert form_messages[0]["mistakes"][0]["type"] == "hip_sag"
    
    @pytest.mark.asyncio
    async def test_handle_pose_data_error_handling(self, mock_websocket, sample_pose_data):
        """Test that handle_pose_data handles errors gracefully."""
        session = WorkoutSession("user123", mock_websocket)
        
        # Mock exercise recognizer to raise exception
        with patch.object(session.exercise_recognizer, 'recognize', side_effect=Exception("Test error")):
            await session.handle_pose_data(sample_pose_data)
        
        # Should send error message
        error_messages = [call[0][0] for call in mock_websocket.send_json.call_args_list 
                         if call[0][0].get("type") == "error"]
        assert len(error_messages) > 0
        assert "error" in error_messages[0]["message"].lower()
    
    def test_cleanup(self, mock_websocket):
        """Test session cleanup."""
        session = WorkoutSession("user123", mock_websocket)
        session.cleanup()
        
        assert session.is_active is False


class TestWebSocketManager:
    """Test WebSocketManager class."""
    
    @pytest.mark.asyncio
    async def test_connect(self, mock_websocket):
        """Test connecting a WebSocket."""
        manager = WebSocketManager()
        
        session = await manager.connect(mock_websocket, "user123")
        
        assert session.user_id == "user123"
        assert "user123" in manager.active_sessions
        mock_websocket.accept.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_replaces_existing_session(self, mock_websocket):
        """Test that connecting replaces existing session for same user."""
        manager = WebSocketManager()
        
        # Connect first session
        session1 = await manager.connect(mock_websocket, "user123")
        
        # Connect second session for same user
        mock_websocket2 = AsyncMock()
        session2 = await manager.connect(mock_websocket2, "user123")
        
        # Should have only one session
        assert len(manager.active_sessions) == 1
        assert manager.active_sessions["user123"] == session2
        assert session1.is_active is False
    
    @pytest.mark.asyncio
    async def test_disconnect(self, mock_websocket):
        """Test disconnecting a WebSocket."""
        manager = WebSocketManager()
        
        # Connect session
        session = await manager.connect(mock_websocket, "user123")
        
        # Disconnect
        await manager.disconnect("user123")
        
        assert "user123" not in manager.active_sessions
        assert session.is_active is False
    
    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_user(self):
        """Test disconnecting a user that doesn't exist."""
        manager = WebSocketManager()
        
        # Should not raise exception
        await manager.disconnect("nonexistent")
    
    @pytest.mark.asyncio
    async def test_get_session(self, mock_websocket):
        """Test getting an active session."""
        manager = WebSocketManager()
        
        # Connect session
        session = await manager.connect(mock_websocket, "user123")
        
        # Get session
        retrieved = manager.get_session("user123")
        
        assert retrieved == session
    
    def test_get_session_nonexistent(self):
        """Test getting a session that doesn't exist."""
        manager = WebSocketManager()
        
        retrieved = manager.get_session("nonexistent")
        
        assert retrieved is None


class TestWebSocketEndpoint:
    """Test WebSocket endpoint integration."""
    
    def test_websocket_endpoint_exists(self):
        """Test that WebSocket endpoint is registered."""
        client = TestClient(app)
        
        # Check that the route exists
        routes = [route.path for route in app.routes]
        assert "/ws/{user_id}" in routes
    
    @pytest.mark.asyncio
    async def test_websocket_message_handling(self):
        """Test WebSocket message handling with TestClient."""
        client = TestClient(app)
        
        with client.websocket_connect("/ws/test_user") as websocket:
            # Send pose data message
            pose_message = {
                "type": "pose_data",
                "keypoints": [
                    {
                        "x": 0.5,
                        "y": 0.5,
                        "z": 0.0,
                        "visibility": 0.9,
                        "name": "nose"
                    }
                    # Add more keypoints as needed
                ],
                "timestamp": 1234567890.0
            }
            
            websocket.send_json(pose_message)
            
            # Should receive some response (exercise detection, etc.)
            # Note: Actual response depends on exercise recognition logic
            # This test just verifies the connection works
    
    @pytest.mark.asyncio
    async def test_websocket_ping_pong(self):
        """Test WebSocket ping/pong for health check."""
        client = TestClient(app)
        
        with client.websocket_connect("/ws/test_user") as websocket:
            # Send ping
            websocket.send_json({"type": "ping"})
            
            # Should receive pong
            response = websocket.receive_json()
            assert response["type"] == "pong"
    
    @pytest.mark.asyncio
    async def test_websocket_invalid_json(self):
        """Test WebSocket handling of invalid JSON."""
        client = TestClient(app)
        
        with client.websocket_connect("/ws/test_user") as websocket:
            # Send invalid JSON
            websocket.send_text("invalid json {")
            
            # Should receive error message
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "format" in response["message"].lower()
