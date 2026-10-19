"""
Verified Exam Syllabus Patterns and Question Weightages.
"""

EXAM_PATTERNS = {
    "MDCAT": {
        "total_mcqs": 180,
        "subjects": {
            "Biology": {"mcqs": 81, "weightage": "45%"},
            "Chemistry": {"mcqs": 45, "weightage": "25%"},
            "Physics": {"mcqs": 36, "weightage": "20%"},
            "English": {"mcqs": 9, "weightage": "5%"},
            "Logical Reasoning": {"mcqs": 9, "weightage": "5%"},
        },
    },
    "ECAT": {
        "total_mcqs": 100,
        "subjects": {
            "Mathematics": {"mcqs": 30, "weightage": "30%"},
            "Physics": {"mcqs": 30, "weightage": "30%"},
            "Chemistry / Computer Science": {"mcqs": 30, "weightage": "30%"},
            "English": {"mcqs": 10, "weightage": "10%"},
        },
    },
   "NUMS": {
        "total_mcqs": 200,
        "subjects": {
            "Biology (Paper-I)": {"mcqs": 55, "weightage": "37.0%"},
            "Chemistry (Paper-I)": {"mcqs": 40, "weightage": "26.5%"},
            "Physics (Paper-I)": {"mcqs": 40, "weightage": "26.5%"},
            "English (Paper-I)": {"mcqs": 15, "weightage": "10.0%"},
            "Psychological Test (Paper-II)": {"mcqs": 50, "weightage": "5.0%"},
        },
        "difficulty": {"Easy": "20%", "Moderate": "60%", "Hard": "20%"},
        "cognitive_split": "70% Recall, 30% Application",
    },
    "NUST NET": {
        "total_mcqs": 200,
        "subjects": {
            "Mathematics": {"mcqs": 80, "weightage": "40%"},
            "Physics": {"mcqs": 60, "weightage": "30%"},
            "Chemistry": {"mcqs": 30, "weightage": "15%"},
            "English": {"mcqs": 20, "weightage": "10%"},
            "Intelligence": {"mcqs": 10, "weightage": "5%"},
        },
    },
}
