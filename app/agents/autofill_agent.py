from app.models import UserProfile
from typing import Dict

class AutofillAgent:
    def __init__(self):
        pass

    def get_form_data(self, profile: UserProfile) -> Dict[str, str]:
        """
        Flattens the complex UserProfile into a simple Key-Value pair 
        mapping that a Browser Extension can easily use.
        """
        data = {
            "first_name": profile.personal_info.name.split()[0] if profile.personal_info.name else "",
            "last_name": profile.personal_info.name.split()[-1] if " " in profile.personal_info.name else "",
            "email": profile.personal_info.email,
            "phone": profile.personal_info.phone or "",
            "linkedin": profile.personal_info.linkedin_url or "",
            "portfolio": profile.personal_info.portfolio_url or "",
        }

        # Add most recent work experience
        if profile.work_history:
            latest = profile.work_history[0]
            data["recent_company"] = latest.company
            data["recent_role"] = latest.role
            data["recent_desc"] = latest.description or ""

        return data