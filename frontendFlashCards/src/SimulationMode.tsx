import React, { useEffect, useState } from "react";
import Flashcardlist from "./SimulationFinale";
import "./styles/SimulationMode.css";

type APIQuestion = {
    question: string;
    options: string[];
    correct_answer: string;
};

type FlashCard = {
    id: number;
    title: string;
    options: string[];
    correctAnswer: string;
};

type AppProps = {
    numQuestions: number;
};

const SimulationMode: React.FC<AppProps> = ({ numQuestions }) => {
    const [cards, setCards] = useState<FlashCard[]>([]);
    const [currentCardIndex, setCurrentCardIndex] = useState(0);
    const [feedback, setFeedback] = useState<string | null>(null);
    const [answers, setAnswers] = useState<number[]>([]);
    const [canAnswer, setCanAnswer] = useState<number>(0);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [loadedQuestions, setLoadedQuestions] = useState(0);

    // Fetch a single question from the API
    const fetchSingleQuestion = async () => {
        const response = await fetch('http://127.0.0.1:8000/questions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                difficulty: "medium"
            })
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch question: ${response.statusText}`);
        }

        return response.json();
    };

    // Initialize with 2 questions
    const initializeQuestions = async () => {
        try {
            setIsLoading(true);
            setError(null);

            // Fetch first two questions sequentially
            const firstQuestion: APIQuestion = await fetchSingleQuestion();
            const secondQuestion: APIQuestion = await fetchSingleQuestion();

            const initialCards = [
                {
                    id: 1,
                    title: firstQuestion.question,
                    options: firstQuestion.options,
                    correctAnswer: firstQuestion.correct_answer
                },
                {
                    id: 2,
                    title: secondQuestion.question,
                    options: secondQuestion.options,
                    correctAnswer: secondQuestion.correct_answer
                }
            ];

            setCards(initialCards);
            setAnswers(new Array(2).fill(-1));
            setLoadedQuestions(2);
        } catch (err) {
            console.error('Fetch error:', err);
            setError(err instanceof Error ? err.message : 'Failed to fetch questions');
        } finally {
            setIsLoading(false);
        }
    };

    // Load next question
    const loadNextQuestion = async () => {
        try {
            if (loadedQuestions < numQuestions) {
                const nextQuestion: APIQuestion = await fetchSingleQuestion();
                const newCard = {
                    id: loadedQuestions + 1,
                    title: nextQuestion.question,
                    options: nextQuestion.options,
                    correctAnswer: nextQuestion.correct_answer
                };

                setCards(prevCards => [...prevCards, newCard]);
                setAnswers(prevAnswers => [...prevAnswers, -1]);
                setLoadedQuestions(prev => prev + 1);
            }
        } catch (err) {
            console.error('Error fetching next question:', err);
            setError('Failed to load next question. Please try again.');
        }
    };

    // Initial load of 2 questions
    useEffect(() => {
        initializeQuestions();
    }, []);

    // Handle moving to next question and loading more if needed
    const handleNext = async () => {
        // If we're not at the last loaded question, just move to next
        if (currentCardIndex < cards.length - 1) {
            setCurrentCardIndex(prev => prev + 1);
            setFeedback(null);
        }
        // If we're at the last loaded question but haven't reached total needed
        else if (loadedQuestions < numQuestions) {
            await loadNextQuestion();
            setCurrentCardIndex(prev => prev + 1);
            setFeedback(null);
        }
        // If we're at the very end
        else if (currentCardIndex === cards.length - 1) {
            if (answers.some(answer => answer === -1)) {
                setFeedback("Please answer all questions before viewing results");
                return;
            }
            setCurrentCardIndex(-1); // Show results
        }
    };

    // Rest of your component code (handlePrevious, handleAnswer, etc.) remains the same
    const handlePrevious = () => {
        setCurrentCardIndex(prev => (prev === 0 ? cards.length - 1 : prev - 1));
        setFeedback(null);
    };

    const handleAnswer = (selectedAnswer: string) => {
        if (canAnswer <= currentCardIndex && canAnswer < cards.length) {
            const currentCard = cards[currentCardIndex];
            const isCorrect = selectedAnswer === currentCard.correctAnswer;

            setAnswers(prev => {
                const newAnswers = [...prev];
                newAnswers[currentCardIndex] = isCorrect ? 1 : 0;
                return newAnswers;
            });

            setFeedback(isCorrect ? "Correct!" : "Incorrect!");
            setCanAnswer(prev => prev + 1);

            // Trigger loading of next question after answering
            if (loadedQuestions < numQuestions) {
                loadNextQuestion();
            }

            handleNext();
        }
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Loading initial questions...</p>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="error-container">
                <h2>Error Loading Questions</h2>
                <p>{error}</p>
                <button
                    onClick={initializeQuestions}
                    className="retry-button"
                >
                    Retry
                </button>
                <button
                    className="back-button"
                    onClick={() => window.location.replace("/start")}
                >
                    Back to Start
                </button>
            </div>
        );
    }

    // Show results or questions
    return currentCardIndex !== -1 ? (
        <div className="app">
            <div className="header">
                <p className="header-text">
                    Question {currentCardIndex + 1} of {numQuestions}
                </p>
                <div className="progress-info">
                    Answered: {canAnswer}/{numQuestions}
                </div>
                <button
                    className="back-button"
                    onClick={() => window.location.replace("/start")}
                >
                    Back
                </button>
            </div>

            <div className="body">
                <div className="flashcard-container">
                    <button
                        className="nav-button"
                        onClick={handlePrevious}
                        disabled={currentCardIndex === 0}
                    >
                        &lt;
                    </button>
                    <FlashCardComponent
                        card={cards[currentCardIndex]}
                        onAnswer={handleAnswer}
                        feedback={feedback}
                        isAnswered={answers[currentCardIndex] !== -1}
                    />
                    <button
                        className="nav-button"
                        onClick={handleNext}
                    >
                        &gt;
                    </button>
                </div>
            </div>
        </div>
    ) : (
        <Flashcardlist cards={cards} answers={answers} />
    );
};


type FlashCardProps = {
    card: FlashCard;
    onAnswer: (selectedAnswer: string) => void;
    feedback: string | null;
    isAnswered: boolean;
};

const FlashCardComponent: React.FC<FlashCardProps> = ({
                                                          card,
                                                          onAnswer,
                                                          feedback,
                                                          isAnswered
                                                      }) => (
    <div className="flashcard">
        <div className="flashcard-header">
            <div className="flashcard-title">{card.title}</div>
        </div>
        <div className="flashcard-options">
            {card.options.map((option, index) => (
                <button
                    key={index}
                    onClick={() => onAnswer(option)}
                    className={`option-button ${isAnswered ? 'answered' : ''}`}
                    disabled={isAnswered}
                >
                    {option}
                </button>
            ))}
        </div>
        {feedback && (
            <div className={`feedback ${
                feedback.includes("Correct") ? "correct" :
                    feedback.includes("Incorrect") ? "incorrect" :
                        "warning"
            }`}>
                {feedback}
            </div>
        )}
    </div>
);

export default SimulationMode;