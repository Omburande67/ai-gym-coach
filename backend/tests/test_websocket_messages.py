"""Unit tests for WebSocket message protocol.

Tests message parsing, validation, and error handling.
Implements Requirements 14.5, 14.6.
"""

import pytest
from pydantic import ValidationError

from app.models.websocket_messages import (
    MessageType,
    PoseDataMessage,
    PingMessage,
    ExerciseDetectedMessage,
    RepCountedMessage,
    FormFeedbackMessage,
    FormMistakeData,
    PongMessage,
    ErrorMessage,
    parse_client_message
)
from app.models.pose import PoseKeypoint


class TestPoseDataMessage:
    """Test PoseDataMessage validation."""
    
    def test_valid_pose_data_message(self):
        """Test creating a valid pose data message."""
        keypoints = [
            PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="nose"),
            PoseKeypoint(x=0.4, y=0.6, z=0.1, visibility=0.8, name="left_eye")
        ]
        
        message = PoseDataMessage(
            keypoints=keypoints,
            timestamp=1234567890.0
        )
        
        assert message.type == MessageType.POSE_DATA
        assert len(message.keypoints) == 2
        assert message.timestamp == 1234567890.0
    
    def test_pose_data_message_validates_coordinates(self):
        """Test that pose data message validates keypoint coordinates."""
        # Invalid x-coordinate (> 1)
        keypoints = [
            PoseKeypoint(x=1.5, y=0.5, z=0.0, visibility=0.9, name="nose")
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            PoseDataMessage(
                keypoints=keypoints,
                timestamp=1234567890.0
            )
        
        assert "x-coordinate must be between 0 and 1" in str(exc_info.value)

    def test_pose_data_message_validates_visibility(self):
        """Test that pose data message validates visibility scores."""
        # Invalid visibility (> 1)
        keypoints = [
            PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=1.5, name="nose")
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            PoseDataMessage(
                keypoints=keypoints,
                timestamp=1234567890.0
            )
        
        assert "visibility must be between 0 and 1" in str(exc_info.value)
    
    def test_pose_data_message_requires_keypoints(self):
        """Test that pose data message requires at least one keypoint."""
        with pytest.raises(ValidationError) as exc_info:
            PoseDataMessage(
                keypoints=[],
                timestamp=1234567890.0
            )
        
        assert "Keypoints list cannot be empty" in str(exc_info.value)
    
    def test_pose_data_message_validates_timestamp(self):
        """Test that pose data message validates timestamp."""
        keypoints = [
            PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="nose")
        ]
        
        # Invalid timestamp (negative)
        with pytest.raises(ValidationError) as exc_info:
            PoseDataMessage(
                keypoints=keypoints,
                timestamp=-1.0
            )
        
        assert "greater than 0" in str(exc_info.value)


class TestPingMessage:
    """Test PingMessage."""
    
    def test_valid_ping_message(self):
        """Test creating a valid ping message."""
        message = PingMessage()
        
        assert message.type == MessageType.PING


class TestExerciseDetectedMessage:
    """Test ExerciseDetectedMessage validation."""
    
    def test_valid_exercise_detected_message(self):
        """Test creating a valid exercise detected message."""
        message = ExerciseDetectedMessage(
            exercise="pushup",
            confidence=0.95
        )
        
        assert message.type == MessageType.EXERCISE_DETECTED
        assert message.exercise == "pushup"
        assert message.confidence == 0.95
    
    def test_exercise_detected_validates_confidence_range(self):
        """Test that confidence must be between 0 and 1."""
        # Confidence > 1
        with pytest.raises(ValidationError) as exc_info:
            ExerciseDetectedMessage(
                exercise="pushup",
                confidence=1.5
            )
        
        assert "less than or equal to 1" in str(exc_info.value)
        
        # Confidence < 0
        with pytest.raises(ValidationError) as exc_info:
            ExerciseDetectedMessage(
                exercise="pushup",
                confidence=-0.1
            )
        
        assert "greater than or equal to 0" in str(exc_info.value)


class TestRepCountedMessage:
    """Test RepCountedMessage validation."""
    
    def test_valid_rep_counted_message(self):
        """Test creating a valid rep counted message."""
        message = RepCountedMessage(
            count=5,
            total=10
        )
        
        assert message.type == MessageType.REP_COUNTED
        assert message.count == 5
        assert message.total == 10
    
    def test_rep_counted_validates_non_negative(self):
        """Test that count and total must be non-negative."""
        # Negative count
        with pytest.raises(ValidationError) as exc_info:
            RepCountedMessage(
                count=-1,
                total=10
            )
        
        assert "greater than or equal to 0" in str(exc_info.value)
        
        # Negative total
        with pytest.raises(ValidationError) as exc_info:
            RepCountedMessage(
                count=5,
                total=-1
            )
        
        assert "greater than or equal to 0" in str(exc_info.value)


class TestFormFeedbackMessage:
    """Test FormFeedbackMessage validation."""
    
    def test_valid_form_feedback_message(self):
        """Test creating a valid form feedback message."""
        mistakes = [
            FormMistakeData(
                type="hip_sag",
                severity=0.6,
                suggestion="Engage your core"
            )
        ]
        
        message = FormFeedbackMessage(
            mistakes=mistakes,
            form_score=85.0
        )
        
        assert message.type == MessageType.FORM_FEEDBACK
        assert len(message.mistakes) == 1
        assert message.form_score == 85.0
    
    def test_form_feedback_validates_score_range(self):
        """Test that form score must be between 0 and 100."""
        mistakes = []
        
        # Score > 100
        with pytest.raises(ValidationError) as exc_info:
            FormFeedbackMessage(
                mistakes=mistakes,
                form_score=150.0
            )
        
        assert "less than or equal to 100" in str(exc_info.value)
        
        # Score < 0
        with pytest.raises(ValidationError) as exc_info:
            FormFeedbackMessage(
                mistakes=mistakes,
                form_score=-10.0
            )
        
        assert "greater than or equal to 0" in str(exc_info.value)
    
    def test_form_feedback_with_empty_mistakes(self):
        """Test form feedback with no mistakes."""
        message = FormFeedbackMessage(
            mistakes=[],
            form_score=100.0
        )
        
        assert len(message.mistakes) == 0
        assert message.form_score == 100.0


class TestFormMistakeData:
    """Test FormMistakeData validation."""
    
    def test_valid_form_mistake(self):
        """Test creating a valid form mistake."""
        mistake = FormMistakeData(
            type="hip_sag",
            severity=0.6,
            suggestion="Engage your core"
        )
        
        assert mistake.type == "hip_sag"
        assert mistake.severity == 0.6
        assert mistake.suggestion == "Engage your core"
    
    def test_form_mistake_validates_severity_range(self):
        """Test that severity must be between 0 and 1."""
        # Severity > 1
        with pytest.raises(ValidationError) as exc_info:
            FormMistakeData(
                type="hip_sag",
                severity=1.5,
                suggestion="Test"
            )
        
        assert "less than or equal to 1" in str(exc_info.value)
        
        # Severity < 0
        with pytest.raises(ValidationError) as exc_info:
            FormMistakeData(
                type="hip_sag",
                severity=-0.1,
                suggestion="Test"
            )
        
        assert "greater than or equal to 0" in str(exc_info.value)


class TestPongMessage:
    """Test PongMessage."""
    
    def test_valid_pong_message(self):
        """Test creating a valid pong message."""
        message = PongMessage()
        
        assert message.type == MessageType.PONG


class TestErrorMessage:
    """Test ErrorMessage validation."""
    
    def test_valid_error_message(self):
        """Test creating a valid error message."""
        message = ErrorMessage(
            message="An error occurred",
            code="TEST_ERROR"
        )
        
        assert message.type == MessageType.ERROR
        assert message.message == "An error occurred"
        assert message.code == "TEST_ERROR"
    
    def test_error_message_without_code(self):
        """Test error message without optional code."""
        message = ErrorMessage(
            message="An error occurred"
        )
        
        assert message.type == MessageType.ERROR
        assert message.message == "An error occurred"
        assert message.code is None


class TestParseClientMessage:
    """Test parse_client_message function."""
    
    def test_parse_pose_data_message(self):
        """Test parsing a pose data message."""
        data = {
            "type": "pose_data",
            "keypoints": [
                {
                    "x": 0.5,
                    "y": 0.5,
                    "z": 0.0,
                    "visibility": 0.9,
                    "name": "nose"
                }
            ],
            "timestamp": 1234567890.0
        }
        
        message = parse_client_message(data)
        
        assert isinstance(message, PoseDataMessage)
        assert message.type == MessageType.POSE_DATA
        assert len(message.keypoints) == 1
    
    def test_parse_ping_message(self):
        """Test parsing a ping message."""
        data = {
            "type": "ping"
        }
        
        message = parse_client_message(data)
        
        assert isinstance(message, PingMessage)
        assert message.type == MessageType.PING
    
    def test_parse_unknown_message_type(self):
        """Test parsing an unknown message type."""
        data = {
            "type": "unknown_type"
        }
        
        with pytest.raises(ValueError) as exc_info:
            parse_client_message(data)
        
        assert "Unknown message type" in str(exc_info.value)
    
    def test_parse_missing_type_field(self):
        """Test parsing a message without type field."""
        data = {
            "keypoints": []
        }
        
        with pytest.raises(ValueError) as exc_info:
            parse_client_message(data)
        
        assert "Unknown message type" in str(exc_info.value)
    
    def test_parse_invalid_message_data(self):
        """Test parsing a message with invalid data."""
        data = {
            "type": "pose_data",
            "keypoints": [],  # Empty keypoints (invalid)
            "timestamp": 1234567890.0
        }
        
        with pytest.raises(ValidationError):
            parse_client_message(data)


class TestMalformedMessageHandling:
    """Test handling of malformed messages."""
    
    def test_handle_invalid_keypoint_coordinates(self):
        """Test handling keypoints with invalid coordinates."""
        data = {
            "type": "pose_data",
            "keypoints": [
                {
                    "x": 2.0,  # Invalid: > 1
                    "y": 0.5,
                    "z": 0.0,
                    "visibility": 0.9,
                    "name": "nose"
                }
            ],
            "timestamp": 1234567890.0
        }
        
        with pytest.raises(ValidationError):
            parse_client_message(data)
    
    def test_handle_missing_required_fields(self):
        """Test handling messages with missing required fields."""
        data = {
            "type": "pose_data",
            # Missing keypoints and timestamp
        }
        
        with pytest.raises(ValidationError):
            parse_client_message(data)
    
    def test_handle_invalid_field_types(self):
        """Test handling messages with invalid field types."""
        data = {
            "type": "pose_data",
            "keypoints": "not a list",  # Should be a list
            "timestamp": 1234567890.0
        }
        
        with pytest.raises(ValidationError):
            parse_client_message(data)
    
    def test_handle_extra_fields(self):
        """Test that extra fields are ignored."""
        data = {
            "type": "ping",
            "extra_field": "should be ignored"
        }
        
        # Should not raise exception
        message = parse_client_message(data)
        assert isinstance(message, PingMessage)
