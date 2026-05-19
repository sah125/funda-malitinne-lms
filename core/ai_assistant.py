# core/ai_assistant.py
import re

class AIAdminAssistant:
    def __init__(self):
        self.user_input = ""
    
    def process(self, user_input):
        self.user_input = user_input.lower().strip()
        
        # Detect commands
        if re.search(r'(show|list|view).*course', self.user_input):
            return self._list_courses()
        
        elif re.search(r'(find|search|get).*student', self.user_input):
            return self._find_student()
        
        elif re.search(r'(update|change|set).*mark|grade', self.user_input):
            return self._update_marks()
        
        elif re.search(r'(enrolled|taking|registered).*course', self.user_input):
            return self._check_enrollment()
        
        elif re.search(r'(stat|dashboard|overview|how many)', self.user_input):
            return self._get_stats()
        
        elif re.search(r'help', self.user_input):
            return self._help()
        
        else:
            return self._unknown()
    
    def _list_courses(self):
        return {
            "action": "list_courses",
            "entity": "course",
            "filters": {},
            "data": {"message": "Fetching all courses..."},
            "confidence": 0.95
        }
    
    def _find_student(self):
        name_match = re.search(r'student\s+([A-Za-z]+)', self.user_input)
        name = name_match.group(1) if name_match else None
        
        return {
            "action": "get_student_info",
            "entity": "student",
            "filters": {"name": name} if name else {},
            "data": {"message": f"Searching for student {name}..." if name else "Which student would you like to find?"},
            "confidence": 0.90
        }
    
    def _update_marks(self):
        name_match = re.search(r'(?:of|for|to)\s+([A-Za-z]+)', self.user_input)
        marks_match = re.search(r'(\d+(?:\.\d+)?)', self.user_input)
        
        name = name_match.group(1) if name_match else None
        marks = float(marks_match.group(1)) if marks_match else None
        
        return {
            "action": "update_marks",
            "entity": "student",
            "filters": {"name": name} if name else {},
            "data": {
                "marks": marks,
                "message": f"Ready to update {name}'s marks to {marks}%" if name and marks else "Please specify student name and marks."
            },
            "confidence": 0.85
        }
    
    def _check_enrollment(self):
        return {
            "action": "check_enrollment",
            "entity": "student",
            "filters": {},
            "data": {"message": "Checking enrollment status..."},
            "confidence": 0.80
        }
    
    def _get_stats(self):
        return {
            "action": "get_stats",
            "entity": "system",
            "filters": {},
            "data": {"message": "Fetching system statistics..."},
            "confidence": 0.98
        }
    
    def _help(self):
        return {
            "action": "help",
            "entity": "system",
            "filters": {},
            "data": {
                "message": """I can help you with:
• "Show me all courses"
• "Find student Tamarah"
• "Update John's marks to 85%"
• "Is Tamarah enrolled?"
• "Show system statistics"
• "Help" for this menu"""
            },
            "confidence": 0.99
        }
    
    def _unknown(self):
        return {
            "action": "unknown",
            "entity": "",
            "filters": {},
            "data": {"message": "I didn't understand. Try 'Help' to see what I can do."},
            "confidence": 0.30
        }