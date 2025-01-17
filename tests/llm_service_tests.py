import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from src.infrastructure.model.llm_service import PhiModelService
from src.domain.models import GenerationRequest, QuestionDifficulty, Question

pytestmark = pytest.mark.asyncio


@pytest.fixture
def llm_service():
    with patch('torch.cuda.is_available', return_value=True), \
            patch('torch.set_default_tensor_type') as mock_tensor_type:
        service = PhiModelService()
        mock_tensor_type.side_effect = None
        service._is_ready = True
        service.vector_store = MagicMock()
        service.llm = AsyncMock()
        return service


@pytest.mark.asyncio
async def test_parse_question_output_valid():
    with patch('torch.cuda.is_available', return_value=True), \
            patch('torch.set_default_tensor_type'):
        service = PhiModelService()
        test_output = """
        Question: What is the capital of France?
        Options:
        A. London
        B. Paris
        C. Berlin
        D. Madrid
        Correct answer: B
        """

        question, options, correct_answer = service.parse_question_output(test_output)
        assert question == "What is the capital of France?"
        assert len(options) == 4
        assert correct_answer == "B"


@pytest.mark.asyncio
async def test_parse_question_output_invalid():
    with patch('torch.cuda.is_available', return_value=True), \
            patch('torch.set_default_tensor_type'):
        service = PhiModelService()
        test_output = "Invalid format"

        question, options, correct_answer = service.parse_question_output(test_output)
        assert question is None
        assert options is None
        assert correct_answer is None


@pytest.mark.asyncio
async def test_get_random_chunk(llm_service):
    test_docs = {'documents': ['test chunk 1', 'test chunk 2']}
    llm_service.vector_store.get.return_value = test_docs

    result = llm_service.get_random_chunk()
    assert result in test_docs['documents']
    llm_service.vector_store.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_random_chunk_empty(llm_service):
    llm_service.vector_store.get.return_value = {'documents': []}

    with pytest.raises(ValueError, match="No documents found in vector store"):
        llm_service.get_random_chunk()


@pytest.mark.asyncio
async def test_generate_question_success(llm_service):
    test_context = "Paris is the capital of France."
    test_llm_output = """
Question: What is the capital of France?
Options:
A. London
B. Paris 
C. Berlin
D. Madrid
Correct answer: B"""

    llm_service.get_random_chunk = Mock(return_value=test_context)

    chain_mock = AsyncMock()
    chain_mock.arun = AsyncMock(return_value=test_llm_output)
    chain_mock.return_final_only = True

    def mock_chain_init(self, llm=None, prompt=None, **kwargs):
        return None

    with patch('langchain.chains.LLMChain.__init__', mock_chain_init), \
            patch('langchain.chains.LLMChain', return_value=chain_mock):
        request = GenerationRequest(topic="test")
        result = await llm_service.generate_question(request)

    assert isinstance(result, Question)
    assert "capital of France" in result.question
    assert len(result.options) == 4
    assert result.correct_answer == "B"

@pytest.mark.asyncio
async def test_generate_question_not_ready(llm_service):
    llm_service._is_ready = False
    request = GenerationRequest(topic="test")

    with pytest.raises(RuntimeError, match="Model not initialized"):
        await llm_service.generate_question(request)


@pytest.mark.asyncio
async def test_generate_question_error_handling(llm_service):
    llm_service.llm.side_effect = Exception("Test error")
    request = GenerationRequest(topic="test")
    result = await llm_service.generate_question(request)

    assert "Error generating question" in result.question
    assert result.correct_answer == "A"