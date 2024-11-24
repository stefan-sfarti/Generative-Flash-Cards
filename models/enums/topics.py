from enum import Enum

class Topic(Enum):
    """Topics"""
    DEFINITION_AND_CLASSIFICATION = "definition_and_classification"
    DIAGNOSIS = "diagnosis"
    ASSESSMENT_OF_HF_SEVERITY = "assessment_of_hf_severity"
    IMAGING_TECHNIQUES = "imaging_techniques"
    DIAGNOSTIC_TESTS = "diagnostic_tests"
    PHARMACOLOGICAL_THERAPY = "pharmacological_therapy"
    DEVICE_THERAPY = "device_therapy"
    COMORBIDITIES = "comorbidities"
    PREVENTION = "prevention"
    END_OF_LIFE_CARE = "end_of_life_care"