# Class Relationships:
# - Question (Abstract Base Class)
#   ├── MultipleChoiceQuestion (Concrete Class)
#   ├── ValueBasedQuestion (Concrete Class)
#   └── OpenEndedQuestion (Concrete Class)
#
# - QuestionFactory (Creates different question types)
#   └── Has-a LLMService (Dependency)
#
# - ResponseGenerator (Generates responses for questions)
#   └── Has-a LLMService (Dependency)
#
# - ResponseCache (Caches responses for questions)
#   └── Used-by QuestionFactory (Association)

from abc import ABC, abstractmethod

from typing import List, Optional, Dict, Union, Tuple
from uuid import UUID, uuid4











