"""Clinical Context Engine for EREN OS.

Manages clinical context building, compression, and validation.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from core.PHASE_1.infrastructure.biomedical.clinical_context.types import (
    ClinicalContext,
    ClinicalEpisode,
    Consultation,
    ContextBuildRequest,
    ContextBuildResult,
    ContextPolicy,
    LabResult,
    Medication,
    Patient,
    PrivacyLevel,
    VitalSigns,
)


class ClinicalContextEngine:
    """Engine for building and managing clinical context.

    Features:
    - Context building from multiple sources
    - Temporal context management
    - Context compression
    - Privacy policy enforcement
    - Validation
    """

    def __init__(self, policy: ContextPolicy | None = None):
        """Initialize clinical context engine.

        Args:
            policy: Default context policy.
        """
        self._policy = policy or ContextPolicy()
        self._patient_cache: dict[str, Patient] = {}
        self._episode_cache: dict[str, list[ClinicalEpisode]] = {}
        self._consultation_cache: dict[str, list[Consultation]] = {}
        self._medication_cache: dict[str, list[Medication]] = {}
        self._vitals_cache: dict[str, list[VitalSigns]] = {}
        self._lab_cache: dict[str, list[LabResult]] = {}

        self._lock = threading.RLock()
        self._data_fetcher: Callable | None = None

    @property
    def policy(self) -> ContextPolicy:
        """Get current policy."""
        return self._policy

    def set_data_fetcher(self, fetcher: Callable) -> None:
        """Set data fetcher function.

        Args:
            fetcher: Async function(data_type, patient_id, **kwargs) -> data
        """
        self._data_fetcher = fetcher

    async def build_context(
        self,
        request: ContextBuildRequest,
    ) -> ContextBuildResult:
        """Build clinical context for a patient.

        Args:
            request: Context build request.

        Returns:
            Context build result.
        """
        start_time = time.time()
        result = ContextBuildResult(request_id=request.request_id)

        try:
            # Fetch patient
            patient = await self._fetch_patient(request.patient_id)
            if not patient:
                result.success = False
                result.error = "Patient not found"
                return result

            result.data_sources_queried.append("patient")
            result.entities_retrieved += 1

            # Build episodes
            episodes = []
            if request.include_episodes:
                episodes = await self._fetch_episodes(request.patient_id, request.max_temporal_days)
                result.data_sources_queried.append("episodes")
                result.entities_retrieved += len(episodes)

            # Build consultations
            consultations = []
            if request.include_consultations:
                consultations = await self._fetch_consultations(request.patient_id, request.max_temporal_days)
                result.data_sources_queried.append("consultations")
                result.entities_retrieved += len(consultations)

            # Build medications
            medications = []
            if request.include_medications:
                medications = await self._fetch_medications(request.patient_id)
                result.data_sources_queried.append("medications")
                result.entities_retrieved += len(medications)

            # Build vitals
            vitals = []
            if request.include_vitals:
                vitals = await self._fetch_vitals(request.patient_id, request.max_temporal_days)
                result.data_sources_queried.append("vitals")
                result.entities_retrieved += len(vitals)

            # Build labs
            labs = []
            if request.include_labs:
                labs = await self._fetch_labs(request.patient_id, request.max_temporal_days)
                result.data_sources_queried.append("labs")
                result.entities_retrieved += len(labs)

            # Get current episode
            current_episode = self._get_current_episode(episodes)

            # Filter active medications
            active_meds = [m for m in medications if m.status == "active"]

            # Calculate temporal range
            temporal_range = self._calculate_temporal_range(episodes, consultations, labs)

            # Calculate relevance
            relevance = self._calculate_relevance(request, episodes, medications, labs)

            # Create context
            context = ClinicalContext(
                context_id=str(uuid.uuid4()),
                patient=patient,
                episodes=episodes,
                consultations=consultations,
                medications=medications,
                allergies=[],  # Would fetch separately
                lab_results=labs,
                vital_signs=vitals,
                current_episode=current_episode,
                active_medications=active_meds,
                temporal_range=temporal_range,
                relevance_score=relevance,
            )

            # Apply privacy policy
            context = self._apply_privacy_policy(context)

            result.context = context
            result.build_time_ms = (time.time() - start_time) * 1000

        except Exception as e:
            result.success = False
            result.error = str(e)
            result.build_time_ms = (time.time() - start_time) * 1000

        return result

    def compress_context(
        self,
        context: ClinicalContext,
        max_tokens: int = 4000,
    ) -> ClinicalContext:
        """Compress clinical context to fit token budget.

        Args:
            context: Full context.
            max_tokens: Maximum tokens allowed.

        Returns:
            Compressed context.
        """
        compressed = ClinicalContext(
            context_id=context.context_id,
            patient=context.patient,
            episodes=context.episodes,
            consultations=[],
            medications=context.active_medications,
            allergies=context.allergies,
            lab_results=self._compress_labs(context.lab_results),
            vital_signs=self._compress_vitals(context.vital_signs),
            current_episode=context.current_episode,
            active_medications=context.active_medications,
            temporal_range=context.temporal_range,
            relevance_score=context.relevance_score,
        )

        # Estimate tokens and further compress if needed
        while self._estimate_tokens(compressed) > max_tokens and compressed.consultations:
            # Remove oldest consultations first
            compressed.consultations = compressed.consultations[-5:]

        return compressed

    def _compress_labs(self, labs: list[LabResult], max_results: int = 10) -> list[LabResult]:
        """Compress lab results to most recent/abnormal."""
        if len(labs) <= max_results:
            return labs

        # Prioritize abnormal results, then most recent
        abnormal = [l for l in labs if l.is_abnormal]
        normal = [l for l in labs if not l.is_abnormal]

        abnormal.sort(key=lambda x: x.resulted_at, reverse=True)
        normal.sort(key=lambda x: x.resulted_at, reverse=True)

        return (abnormal[:max_results] + normal[:max_results - len(abnormal)])[:max_results]

    def _compress_vitals(self, vitals: list[VitalSigns], max_results: int = 5) -> list[VitalSigns]:
        """Compress vital signs to most recent."""
        if len(vitals) <= max_results:
            return vitals

        sorted_vitals = sorted(vitals, key=lambda x: x.recorded_at, reverse=True)
        return sorted_vitals[:max_results]

    def validate_context(self, context: ClinicalContext) -> tuple[bool, list[str]]:
        """Validate clinical context.

        Args:
            context: Context to validate.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []

        # Check patient
        if not context.patient.patient_id:
            errors.append("Patient ID is required")

        # Check episode consistency
        for episode in context.episodes:
            if episode.patient_id != context.patient.patient_id:
                errors.append(f"Episode {episode.episode_id} belongs to different patient")

        # Check consultation consistency
        for consult in context.consultations:
            if consult.patient_id != context.patient.patient_id:
                errors.append(f"Consultation {consult.consultation_id} belongs to different patient")

        # Check medication consistency
        for med in context.medications:
            if med.patient_id != context.patient.patient_id:
                errors.append(f"Medication {med.medication_id} belongs to different patient")

        # Check temporal consistency
        if context.temporal_range:
            start, end = context.temporal_range
            if start > end:
                errors.append("Temporal range start is after end")

        return len(errors) == 0, errors

    def _apply_privacy_policy(self, context: ClinicalContext) -> ClinicalContext:
        """Apply privacy policy to context."""
        policy = self._policy

        if policy.mask_identifiers:
            # Create de-identified copy
            patient = Patient(
                patient_id=f"ANON_{context.patient.patient_id[:8]}",
                mrn="",
                first_name="[REDACTED]",
                last_name="[REDACTED]",
                date_of_birth=None,  # Redact DOB
                allergies=context.patient.allergies,
            )
            context = ClinicalContext(
                context_id=context.context_id,
                patient=patient,
                episodes=context.episodes,
                consultations=context.consultations,
                medications=context.medications,
                allergies=context.allergies,
                lab_results=context.lab_results,
                vital_signs=context.vital_signs,
                current_episode=context.current_episode,
                active_medications=context.active_medications,
                temporal_range=context.temporal_range,
                relevance_score=context.relevance_score,
            )

        return context

    def _calculate_relevance(
        self,
        request: ContextBuildRequest,
        episodes: list[ClinicalEpisode],
        medications: list[Medication],
        labs: list[LabResult],
    ) -> float:
        """Calculate context relevance score."""
        score = 0.5  # Base score

        # Recent activity boost
        recent_episodes = sum(1 for e in episodes if self._is_recent(e.admission_date, 30))
        score += min(recent_episodes * 0.1, 0.3)

        # Active medications
        active_meds = sum(1 for m in medications if m.status == "active")
        score += min(active_meds * 0.05, 0.2)

        # Abnormal labs
        abnormal_labs = sum(1 for l in labs if l.is_abnormal)
        score += min(abnormal_labs * 0.1, 0.2)

        return min(score, 1.0)

    def _is_recent(self, dt: datetime, days: int) -> bool:
        """Check if datetime is within recent days."""
        if not dt:
            return False
        cutoff = datetime.now(UTC) - timedelta(days=days)
        return dt > cutoff

    def _calculate_temporal_range(
        self,
        episodes: list[ClinicalEpisode],
        consultations: list[Consultation],
        labs: list[LabResult],
    ) -> tuple[datetime, datetime] | None:
        """Calculate temporal range of context."""
        all_dates = []

        for e in episodes:
            all_dates.append(e.admission_date)
            if e.discharge_date:
                all_dates.append(e.discharge_date)

        for c in consultations:
            all_dates.append(c.date)

        for l in labs:
            all_dates.append(l.collected_at)

        if not all_dates:
            return None

        return (min(all_dates), max(all_dates))

    def _get_current_episode(self, episodes: list[ClinicalEpisode]) -> ClinicalEpisode | None:
        """Get the most recent active episode."""
        active = [e for e in episodes if e.status == "active"]
        if active:
            return max(active, key=lambda e: e.admission_date)
        return None

    def _estimate_tokens(self, context: ClinicalContext) -> int:
        """Estimate token count for context."""
        # Rough estimate: ~4 chars per token
        text = str(context.to_dict())
        return len(text) // 4

    # =========================================================================
    # Data Fetching (stub implementations)
    # =========================================================================

    async def _fetch_patient(self, patient_id: str) -> Patient | None:
        """Fetch patient data."""
        if self._data_fetcher:
            return await self._data_fetcher("patient", patient_id)
        return Patient(patient_id=patient_id, first_name="John", last_name="Doe")

    async def _fetch_episodes(self, patient_id: str, days: int) -> list[ClinicalEpisode]:
        """Fetch episodes."""
        if self._data_fetcher:
            return await self._data_fetcher("episodes", patient_id, days=days)
        return []

    async def _fetch_consultations(self, patient_id: str, days: int) -> list[Consultation]:
        """Fetch consultations."""
        if self._data_fetcher:
            return await self._data_fetcher("consultations", patient_id, days=days)
        return []

    async def _fetch_medications(self, patient_id: str) -> list[Medication]:
        """Fetch medications."""
        if self._data_fetcher:
            return await self._data_fetcher("medications", patient_id)
        return []

    async def _fetch_vitals(self, patient_id: str, days: int) -> list[VitalSigns]:
        """Fetch vital signs."""
        if self._data_fetcher:
            return await self._data_fetcher("vitals", patient_id, days=days)
        return []

    async def _fetch_labs(self, patient_id: str, days: int) -> list[LabResult]:
        """Fetch lab results."""
        if self._data_fetcher:
            return await self._data_fetcher("labs", patient_id, days=days)
        return []


# =============================================================================
# Singleton
# =============================================================================

_global_engine: ClinicalContextEngine | None = None
_engine_lock = threading.Lock()


def get_clinical_context_engine() -> ClinicalContextEngine:
    """Get global clinical context engine."""
    global _global_engine
    with _engine_lock:
        if _global_engine is None:
            _global_engine = ClinicalContextEngine()
        return _global_engine


def reset_clinical_context_engine() -> None:
    """Reset global engine."""
    global _global_engine
    with _engine_lock:
        _global_engine = None
