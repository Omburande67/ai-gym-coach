"""Repetition counting service using state machine + oscillation logic.

For large-movement exercises (push-up, squat, jumping jack):
  Uses joint angle thresholds and state machine (UP / DOWN).

For small-movement exercises (hand rotation, neck rotation):
  Uses wrist/nose X-position oscillation tracking — detects direction
  reversals which each represent one rotation rep.
"""

import math
from enum import Enum
from typing import Callable, List, Optional
from app.models.exercise import ExerciseType
from app.models.pose import PoseData
from app.utils.biomechanics import (
    calculate_joint_angles, calculate_neck_angle,
    get_average_angle, get_keypoint_by_name
)


class RepPhase(Enum):
    """Exercise phase states for rep counting."""
    UP = "up"
    DOWN = "down"
    TRANSITION = "transition"


class RepCounter:
    """
    State machine + oscillation-based repetition counter.
    """

    def __init__(self, exercise_type: ExerciseType):
        self.exercise_type = exercise_type
        self.count = 0

        # Initial phase
        if exercise_type in [ExerciseType.JUMPING_JACK]:
            self.current_phase = RepPhase.DOWN
        else:
            self.current_phase = RepPhase.UP

        self.last_transition_time = 0.0
        self.hysteresis_buffer = 8       # degrees
        self.min_rep_duration = 0.4      # seconds between reps

        # Plank tracking
        self.start_time: Optional[float] = None
        self.duration_seconds = 0.0

        # ── Oscillation tracker state (for hand/neck rotation) ──────────
        # Rolling signal buffer
        self._osc_window: List[float] = []
        self._osc_window_size = 20        # frames to compute adaptive mean
        # Direction state
        self._osc_last_dir: Optional[str] = None   # 'pos' or 'neg'
        # Half-cycle flag (need pos→neg OR neg→pos to count 1 rep)
        self._osc_half_done = False
        self._osc_last_count_time = 0.0

    # ── Public API ──────────────────────────────────────────────────────

    def update(self, pose_data: PoseData) -> Optional[int]:
        """Process one frame. Returns new count if a rep completed."""
        t = pose_data.timestamp / 1000  # ms → seconds

        if self.exercise_type == ExerciseType.PLANK:
            return self._update_plank(t)

        if self.exercise_type == ExerciseType.HAND_ROTATION:
            return self._update_osc(t, pose_data,
                                    signal_fn=self._wrist_x_signal,
                                    threshold=0.018,
                                    min_gap=0.25)

        if self.exercise_type == ExerciseType.NECK_ROTATION:
            return self._update_osc(t, pose_data,
                                    signal_fn=self._nose_x_signal,
                                    threshold=0.025,
                                    min_gap=0.25)

        # Angle-based exercises (pushup, squat, jumping jack)
        angles = calculate_joint_angles(pose_data)
        primary = self._primary_angle(angles)
        if primary is None:
            return None

        new_phase = self._angle_transition(primary)
        if new_phase == self.current_phase:
            return None

        dt = t - self.last_transition_time
        self.current_phase = new_phase
        self.last_transition_time = t

        rep_done = False
        if self.exercise_type == ExerciseType.JUMPING_JACK:
            # DOWN → UP → DOWN = 1 rep
            rep_done = (new_phase == RepPhase.DOWN and dt >= self.min_rep_duration / 2)
        else:
            # pushup / squat: UP → DOWN → UP = 1 rep
            rep_done = (new_phase == RepPhase.UP and dt >= self.min_rep_duration / 2)

        if rep_done:
            self.count += 1
            return self.count
        return None

    def get_count(self) -> int:
        return self.count

    def get_duration(self) -> float:
        return self.duration_seconds

    def reset(self) -> None:
        self.count = 0
        self.current_phase = RepPhase.DOWN if self.exercise_type in [
            ExerciseType.JUMPING_JACK, ExerciseType.HAND_ROTATION,
            ExerciseType.NECK_ROTATION
        ] else RepPhase.UP
        self.last_transition_time = 0.0
        self.start_time = None
        self.duration_seconds = 0.0
        self._osc_window.clear()
        self._osc_last_dir = None
        self._osc_half_done = False
        self._osc_last_count_time = 0.0

    # ── Oscillation engine ──────────────────────────────────────────────

    def _update_osc(
        self, t: float, pose_data: PoseData,
        signal_fn: Callable, threshold: float, min_gap: float
    ) -> Optional[int]:
        """
        Count reps by detecting direction reversals in a 1D signal.
        Each full reversal cycle (pos→neg or neg→pos) = 1 rep.
        """
        val = signal_fn(pose_data)
        if val is None:
            return None

        self._osc_window.append(val)
        if len(self._osc_window) > self._osc_window_size:
            self._osc_window.pop(0)

        if len(self._osc_window) < 6:
            return None

        baseline = sum(self._osc_window) / len(self._osc_window)
        dev = val - baseline

        # Classify current direction
        if dev > threshold:
            cur_dir = 'pos'
        elif dev < -threshold:
            cur_dir = 'neg'
        else:
            return None  # dead zone — don't update direction

        if cur_dir == self._osc_last_dir:
            return None  # still moving same direction

        # Direction changed
        prev_dir = self._osc_last_dir
        self._osc_last_dir = cur_dir

        if prev_dir is None:
            return None  # first direction — just record it

        # We have a reversal: prev_dir → cur_dir
        # Count 1 rep per full cycle (2 reversals)
        self._osc_half_done = not self._osc_half_done
        if self._osc_half_done:
            return None  # only half a cycle done

        # Full cycle complete — check min time gap
        if (t - self._osc_last_count_time) < min_gap:
            self._osc_half_done = False  # reset to avoid phantom count
            return None

        self.count += 1
        self._osc_last_count_time = t
        return self.count

    # ── Signal extractors ───────────────────────────────────────────────

    def _wrist_x_signal(self, pose_data: PoseData) -> Optional[float]:
        """
        Wrist-to-elbow horizontal offset.
        During hand rotations the wrist oscillates left/right relative to elbow.
        """
        lw = get_keypoint_by_name(pose_data, 'left_wrist')
        le = get_keypoint_by_name(pose_data, 'left_elbow')
        rw = get_keypoint_by_name(pose_data, 'right_wrist')
        re = get_keypoint_by_name(pose_data, 'right_elbow')

        vals = []
        if lw and le and lw.visibility > 0.35 and le.visibility > 0.35:
            vals.append(lw.x - le.x)
        if rw and re and rw.visibility > 0.35 and re.visibility > 0.35:
            # Mirror right side so both move in same direction
            vals.append(-(rw.x - re.x))

        if not vals:
            return None
        return sum(vals) / len(vals)

    def _nose_x_signal(self, pose_data: PoseData) -> Optional[float]:
        """
        Nose horizontal offset from shoulder midpoint.
        During neck rotations the nose sweeps left/right.
        """
        nose = get_keypoint_by_name(pose_data, 'nose')
        ls   = get_keypoint_by_name(pose_data, 'left_shoulder')
        rs   = get_keypoint_by_name(pose_data, 'right_shoulder')
        if not (nose and ls and rs):
            return None
        if nose.visibility < 0.4:
            return None
        mid_x = (ls.x + rs.x) / 2
        return nose.x - mid_x

    # ── Angle-based helpers ─────────────────────────────────────────────

    def _primary_angle(self, angles: dict) -> Optional[float]:
        if self.exercise_type == ExerciseType.PUSHUP:
            return get_average_angle(angles.get('left_elbow'), angles.get('right_elbow'))
        elif self.exercise_type == ExerciseType.SQUAT:
            return get_average_angle(angles.get('left_knee'), angles.get('right_knee'))
        elif self.exercise_type == ExerciseType.JUMPING_JACK:
            return get_average_angle(angles.get('left_shoulder'), angles.get('right_shoulder'))
        return None

    def _angle_transition(self, angle: float) -> RepPhase:
        if self.exercise_type == ExerciseType.PUSHUP:
            if self.current_phase == RepPhase.UP and angle < 90 + self.hysteresis_buffer:
                return RepPhase.DOWN
            if self.current_phase == RepPhase.DOWN and angle > 160 - self.hysteresis_buffer:
                return RepPhase.UP

        elif self.exercise_type == ExerciseType.SQUAT:
            if self.current_phase == RepPhase.UP and angle < 90 + self.hysteresis_buffer:
                return RepPhase.DOWN
            if self.current_phase == RepPhase.DOWN and angle > 160 - self.hysteresis_buffer:
                return RepPhase.UP

        elif self.exercise_type == ExerciseType.JUMPING_JACK:
            if self.current_phase == RepPhase.DOWN and angle > 160 - self.hysteresis_buffer:
                return RepPhase.UP
            if self.current_phase == RepPhase.UP and angle < 30 + self.hysteresis_buffer:
                return RepPhase.DOWN

        return self.current_phase

    # ── Plank ───────────────────────────────────────────────────────────

    def _update_plank(self, t: float) -> Optional[int]:
        if self.start_time is None:
            self.start_time = t
        self.duration_seconds = t - self.start_time
        return None
