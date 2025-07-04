"""
Employee domain model
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Employee:
    """Employee class"""

    id: str
    name: str
    skills: set[str] = field(default_factory=set)
    # Employee preference fields
    preferred_days_off: set[str] = field(
        default_factory=set
    )  # e.g., {"friday", "saturday"}
    preferred_work_days: set[str] = field(
        default_factory=set
    )  # e.g., {"sunday", "monday"}
    unavailable_dates: set[datetime] = field(
        default_factory=set
    )  # Specific dates (hard constraint)
    # Emergency addition tracking
    is_emergency_addition: bool = field(default=False)
    emergency_added_at: datetime | None = field(default=None)

    def has_skill(self, skill: str) -> bool:
        """Check if employee has the specified skill"""
        return skill in self.skills

    def has_all_skills(self, required_skills: set[str]) -> bool:
        """Check if employee has all required skills"""
        return required_skills.issubset(self.skills)

    def prefers_day_off(self, day_name: str) -> bool:
        """Check if employee prefers this day off"""
        if self.preferred_days_off is None or len(self.preferred_days_off) == 0:
            return False
        day_lower = day_name.lower()
        for pref_day in self.preferred_days_off:
            if pref_day is not None and pref_day.lower() == day_lower:
                return True
        return False

    def prefers_work_day(self, day_name: str) -> bool:
        """Check if employee prefers to work on this day"""
        if self.preferred_work_days is None or len(self.preferred_work_days) == 0:
            return False
        day_lower = day_name.lower()
        for pref_day in self.preferred_work_days:
            if pref_day is not None and pref_day.lower() == day_lower:
                return True
        return False

    def is_unavailable_on_date(self, date: datetime) -> bool:
        """Check if employee is unavailable on a specific date"""
        # Handle None or empty unavailable_dates safely
        if self.unavailable_dates is None or len(self.unavailable_dates) == 0:
            return False

        # Normalize the input date to date-only (remove time components)
        date_only = date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Check each unavailable date explicitly to avoid generator expression issues
        for unavailable_date in self.unavailable_dates:
            if unavailable_date is None:
                continue
            unavailable_only = unavailable_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            if unavailable_only == date_only:
                return True

        return False

    def mark_as_emergency_addition(self) -> None:
        """Mark employee as emergency addition"""
        self.is_emergency_addition = True
        self.emergency_added_at = datetime.now()

    def has_required_skills(self, required_skills: set[str]) -> bool:
        """Check if employee has all required skills"""
        return required_skills.issubset(self.skills)

    def __str__(self):
        return f"Employee(id='{self.id}', name='{self.name}', skills={self.skills})"
