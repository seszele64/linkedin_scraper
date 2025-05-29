from enum import IntEnum

class WorkplaceType(IntEnum):
    """LinkedIn workplace type filter values"""
    ON_SITE = 1
    REMOTE = 2
    HYBRID = 3
    
    @property
    def label(self):
        """Return human-readable label for the workplace type"""
        labels = {
            WorkplaceType.ON_SITE: "On-site",
            WorkplaceType.REMOTE: "Remote", 
            WorkplaceType.HYBRID: "Hybrid"
        }
        return labels[self]

class ExperienceLevel(IntEnum):
    """LinkedIn experience level filter values"""
    INTERNSHIP = 1
    ENTRY_LEVEL = 2
    ASSOCIATE = 3
    MID_SENIOR = 4
    DIRECTOR = 5
    EXECUTIVE = 6
    
    @property
    def label(self):
        """Return human-readable label for the experience level"""
        labels = {
            ExperienceLevel.INTERNSHIP: "Internship",
            ExperienceLevel.ENTRY_LEVEL: "Entry level",
            ExperienceLevel.ASSOCIATE: "Associate", 
            ExperienceLevel.MID_SENIOR: "Mid-Senior level",
            ExperienceLevel.DIRECTOR: "Director",
            ExperienceLevel.EXECUTIVE: "Executive"
        }
        return labels[self]