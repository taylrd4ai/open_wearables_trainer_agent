"""Client profile, benchmarks, and training templates for Eric Taylor.

Source: fitness_coaching_handoff.docx (2026-09-21).
This is the single source of truth for exercise prescriptions, load
benchmarks, and the weekly schedule. The recommendation engine reads
from here rather than hardcoding values inline.
"""

from typing import Any, Dict, List

CLIENT_PROFILE: Dict[str, Any] = {
    "name": "Eric Taylor",
    "age": 41,
    "sex": "male",
    "height_ft": 6,
    "weight_lb": 195,
    "activity_baseline": "desk-based, sedentary outside training (~4000 steps/day)",
    "primary_goals": [
        "sustainable full-body strength habit",
        "mobility/resilience for competitive soccer",
        "aerobic base / VO2 max",
    ],
    "main_sport": "competitive soccer",
    "secondary_sports": ["golf", "swimming"],
    "behavioral_notes": (
        "Task initiation can be difficult. Prescriptions should be short, "
        "explicit, low-friction, and offer a viable home fallback."
    ),
    "coaching_style": "exact exercises, sets, reps, duration, load-adjustment rules, data-driven adaptation",
    "wearables": {
        "preferred": "garmin",
        "connected_via": "whoop_through_open_wearables",
    },
}

INJURY_CONTEXT: Dict[str, Any] = {
    "history_2025": ["patellar dislocation", "partial quadriceps tear", "ankle sprain"],
    "clearance": "Cleared by physician for competitive soccer; currently no pain.",
    "benign_symptoms": ["non-painful knee clicking", "non-painful hip clicking"],
    "priorities": [
        "quad/hamstring strength",
        "knee tracking",
        "ankle balance/proprioception",
        "calf strength",
        "hip control",
        "trunk anti-rotation",
    ],
    "escalation_triggers": [
        "pain",
        "swelling",
        "locking or catching",
        "giving-way",
        "recurrent patellar shift/instability",
        "altered gait",
        "symptoms worse the next day",
    ],
    "escalation_action": "Stop aggravating activity; recommend clinical reassessment (sports PT/orthopedics).",
}

WEEKLY_SCHEDULE: Dict[str, str] = {
    "monday": "zone2_cardio_25_35min_optional_home_stability",
    "tuesday": "competitive_soccer_60_90min_high_strain",
    "wednesday": "gym_available_recovery_focused_default",
    "thursday": "gym_available_primary_strength",
    "friday": "gym_available_optional_second_session",
    "saturday": "zone2_cardio_30_45min",
    "sunday": "rest_walk_or_short_home_mobility",
}

EQUIPMENT: Dict[str, List[str]] = {
    "gym_wed_thu_fri": [
        "dumbbells",
        "leg_press",
        "leg_extension",
        "seated_hamstring_curl",
        "chest_press",
        "row",
        "lat_pulldown",
        "hip_abduction_machine",
        "assisted_pull_up",
        "keiser_infinity",
    ],
    "home": ["resistance_bands", "bodyweight"],
}

# Calibration was 8 reps at listed RPE. Working prescription is the
# conservative starting point derived from that calibration.
LOAD_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "leg_press": {"calibration_lb": 190, "calibration_rpe": 7, "working_lb": 190, "working_sets_reps": "1-2x8"},
    "seated_row": {"calibration_lb": 80, "calibration_rpe": 6, "working_lb": 80, "working_sets_reps": "1-2x8-10"},
    "chest_press": {"calibration_lb": 100, "calibration_rpe": 6, "working_lb": 100, "working_sets_reps": "1-2x8-10"},
    "seated_hamstring_curl": {"calibration_lb": 80, "calibration_rpe": 8, "working_lb": 70, "working_sets_reps": "1-2x8-10"},
    "lat_pulldown": {"calibration_lb": 80, "calibration_rpe": 6, "working_lb": 80, "working_sets_reps": "1-2x8-10"},
    "overhead_press": {"calibration_lb": 80, "calibration_rpe": 6, "working_lb": 80, "working_sets_reps": "1-2x8-10"},
    # Not yet calibrated — engine should instruct "calibrate at RPE 6-7" for these.
    "rdl": {"calibration_lb": None, "calibration_rpe": None, "working_lb": None, "working_sets_reps": "calibrate_rpe_6_7"},
    "goblet_squat": {"calibration_lb": None, "calibration_rpe": None, "working_lb": None, "working_sets_reps": "calibrate_rpe_6_7"},
    "step_up": {"calibration_lb": None, "calibration_rpe": None, "working_lb": None, "working_sets_reps": "calibrate_rpe_6_7"},
    "hip_abduction": {"calibration_lb": None, "calibration_rpe": None, "working_lb": None, "working_sets_reps": "calibrate_rpe_6_7"},
    "calf_raise": {"calibration_lb": None, "calibration_rpe": None, "working_lb": None, "working_sets_reps": "calibrate_rpe_6_7"},
    "pallof_press": {"calibration_lb": None, "calibration_rpe": None, "working_lb": None, "working_sets_reps": "calibrate_rpe_6_7"},
    "external_rotation": {"calibration_lb": None, "calibration_rpe": None, "working_lb": None, "working_sets_reps": "calibrate_rpe_6_7"},
}

PROGRESSION_RULES: Dict[str, Any] = {
    "target_rpe": "6-7",
    "reps_in_reserve": "2-4",
    "weeks_1_2_sets": "1-2 per exercise",
    "steady_state_sets": "2 per exercise; 3 only once recovery/form/adherence stable",
    "progress_condition": "top rep target hit at RPE 6-7 with controlled form for two consecutive sessions",
    "typical_increase_upper_lb": "5-10",
    "typical_increase_leg_press_curl_lb": "10-20",
    "typical_increase_dumbbell": "smallest available increment",
    "regression_condition": "RPE >= 8, form breakdown, pain/instability, or symptoms worse next day",
    "regression_action": "reduce load 10-20% or remove one set",
    "avoid": ["max testing", "training to failure", "extra plyometrics/sprints outside soccer (initially)"],
}

# Each template is a list of {exercise, dose, cue} in prescribed order.
MACHINE_TEMPLATE: List[Dict[str, str]] = [
    {"exercise": "leg_press", "dose": "190 lb; 1-2x8", "cue": "Controlled depth; knees follow toes"},
    {"exercise": "seated_hamstring_curl", "dose": "70 lb; 1-2x8-10", "cue": "2-3 second lowering"},
    {"exercise": "leg_extension", "dose": "calibrate; 1-2x10", "cue": "Pain-free range; controlled contraction"},
    {"exercise": "chest_press", "dose": "100 lb; 1-2x8-10", "cue": "Smooth, pain-free press"},
    {"exercise": "seated_row", "dose": "80 lb; 1-2x8-10", "cue": "No shrugging or torso swing"},
    {"exercise": "lat_pulldown_or_assisted_pullup", "dose": "80 lb / calibrate; 1-2x8", "cue": "No trunk swing"},
    {"exercise": "keiser_pallof_press", "dose": "calibrate; 1-2x8/side", "cue": "Resist rotation"},
    {"exercise": "hip_abduction_machine", "dose": "calibrate; 1-2x12", "cue": "Level pelvis"},
    {"exercise": "single_leg_calf_raise", "dose": "BW; 2x10/side", "cue": "Full range, slow lower"},
    {"exercise": "single_leg_balance", "dose": "2x20-30sec/side", "cue": "Near support"},
]

DUMBBELL_TEMPLATE: List[Dict[str, str]] = [
    {"exercise": "goblet_box_squat", "dose": "15-25 lb; 1-2x8", "cue": "Box/bench; stable knees"},
    {"exercise": "db_romanian_deadlift", "dose": "15-20 lb each; 1-2x8", "cue": "Hips back; neutral spine"},
    {"exercise": "db_bench_or_floor_press", "dose": "15-25 lb each; 1-2x8", "cue": "Pain-free shoulder range"},
    {"exercise": "one_arm_db_row", "dose": "20-30 lb; 1-2x8/side", "cue": "Brace; resist rotation"},
    {"exercise": "seated_db_overhead_press", "dose": "10-15 lb each; 1-2x8", "cue": "Ribs down; no back arch"},
    {"exercise": "low_step_up", "dose": "BW; 1-2x8/side", "cue": "Quiet, controlled descent"},
    {"exercise": "suitcase_carry", "dose": "20-30 lb; 2x30sec/side", "cue": "Tall posture; no lean"},
    {"exercise": "single_leg_calf_raise", "dose": "BW; 2x10/side", "cue": "Full height"},
    {"exercise": "single_leg_balance", "dose": "2x20-30sec/side", "cue": "Near support"},
]

HOME_TEMPLATE: List[Dict[str, str]] = [
    {"exercise": "chair_squat", "dose": "2x10", "cue": "Slow lower; stable knee path"},
    {"exercise": "banded_good_morning", "dose": "2x12", "cue": "Hips back; brace trunk"},
    {"exercise": "incline_push_up", "dose": "2x8-12", "cue": "Counter/table; 2 reps in reserve"},
    {"exercise": "banded_row", "dose": "2x12", "cue": "Secure anchor; elbows toward hips"},
    {"exercise": "banded_lateral_walk", "dose": "2x8 steps each way", "cue": "Shallow athletic stance"},
    {"exercise": "banded_hamstring_curl", "dose": "2x12/side", "cue": "Slow return"},
    {"exercise": "banded_ankle_eversion", "dose": "2x12/side", "cue": "Controlled outward ankle motion"},
    {"exercise": "pallof_press", "dose": "2x10/side", "cue": "Resist rotation"},
    {"exercise": "single_leg_balance", "dose": "2x20-30sec/side", "cue": "Use support as needed"},
]

RECOVERY_CARDIO: Dict[str, Any] = {
    "tuesday_strain_note": "Competitive soccer is very high strain (historical WHOOP strain 18-20 vs average ~6).",
    "wednesday_default": "20-30 min easy Zone 2 plus light core/mobility",
    "preferred_recovery_content": [
        "light core (dead bug, bird-dog, Pallof)",
        "pain-free hip/ankle/thoracic mobility",
        "easy walking/cycling/elliptical",
    ],
    "zone2_schedule": {
        "monday_min": "25-35",
        "wednesday_min": "20-25",
        "saturday_min": "30-45",
    },
    "zone2_intensity_rpe": "3-4",
    "zone2_progression": "increase only one Zone 2 session by 5 min/week when recovery and joints are good",
    "vo2_option": {
        "eligibility": "after 4-6 stable weeks",
        "protocol": "bike 4x2min at RPE 8/10 with 2min easy between",
        "placement": "away from Tuesday soccer",
    },
}

# The core "Agent Decision Rules" table — this drives recommend_workout().
AGENT_DECISION_RULES: List[Dict[str, str]] = [
    {"situation": "day_after_soccer_or_poor_readiness", "prescription": "recovery_default_no_hard_lower_body"},
    {"situation": "good_readiness_thursday", "prescription": "machine_template_primary_strength"},
    {"situation": "good_readiness_friday", "prescription": "machine_or_dumbbell_template_1_2_sets_if_soccer_fatigue"},
    {"situation": "home_no_equipment_time_constrained", "prescription": "home_template_do_not_replace_with_inactivity"},
    {"situation": "high_fatigue_poor_sleep_or_soreness", "prescription": "zone2_only_mobility_light_core_walking"},
    {"situation": "pain_swelling_locking_instability_patellar_symptoms", "prescription": "stop_and_escalate_clinical"},
    {"situation": "top_reps_at_rpe_leq7_two_sessions", "prescription": "increase_load_next_exposure"},
    {"situation": "rpe_geq8_or_poor_form", "prescription": "maintain_or_reduce_load_do_not_progress"},
]

TRACKING_REQUIREMENTS: List[str] = [
    "date, template, exercise, load, sets, reps, RPE, pain (0-10), joint/form notes",
    "soccer duration and subjective intensity; check next-day readiness before Wednesday prescription",
    "weekly Zone 2 minutes and step average; build from ~4000 daily steps gradually",
    "Garmin/WHOOP readiness and load data when available (Garmin preferred; WHOOP via Open Wearables)",
    "periodic bodyweight, energy, sleep/recovery, and joint symptom changes",
]
