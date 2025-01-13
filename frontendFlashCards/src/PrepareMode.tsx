import React, { useEffect, useState } from "react";
 // Importă useNavigate
import "./PrepareMode.css";
import questions from "./questions.json";

type Question = {
    id: number;
    question: string;
    answers: string[];
    correctAnswer: string;
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

const PrepareMode: React.FC<AppProps> = ({ numQuestions }) => {
    const [cards, setCards] = useState<FlashCard[]>([]);
    const [currentCardIndex, setCurrentCardIndex] = useState(0);
    const [feedback, setFeedback] = useState<string | null>(null);


    useEffect(() => {
        const flashCards = questions.slice(0, numQuestions).map((q: Question) => ({
            id: q.id,
            title: q.question,
            options: q.answers,
            correctAnswer: q.correctAnswer,
        }));

        setCards(flashCards);
    }, [numQuestions]);

    const handleNext = () => {
        setCurrentCardIndex((prev) => (prev === cards.length - 1 ? 0 : prev + 1));
        setFeedback(null);
    };

    const handlePrevious = () => {
        setCurrentCardIndex((prev) => (prev === 0 ? cards.length - 1 : prev - 1));
        setFeedback(null);
    };

    const handleAnswer = (selectedAnswer: string) => {
        const currentCard = cards[currentCardIndex];
        if (selectedAnswer === currentCard.correctAnswer) {
            setFeedback("Correct!");
        } else {
            setFeedback(`Incorrect! The correct answer is: ${currentCard.correctAnswer}`);
        }
    };

    return (
        <div className="app">
            <header className="header">
                <button
                    className="back-button"
                    onClick={() => window.location.replace("/start")}
                >
                    Back
                </button>
                <p className="header-text">Flash Card 1 </p>
            </header>
            {cards.length > 0 ? (
                <div className="body">
                    <div className="flashcard-container">
                        <button className="nav-button" onClick={handlePrevious}>
                            &lt;
                        </button>
                        <FlashCardComponent
                            card={cards[currentCardIndex]}
                            onAnswer={handleAnswer}
                            feedback={feedback}
                        />
                        <button className="nav-button" onClick={handleNext}>
                            &gt;
                        </button>
                    </div>
                </div>
            ) : (
                <div className="no-flashcards">No flashcards available</div>
            )}
        </div>
    );
};

type FlashCardProps = {
    card: FlashCard;
    onAnswer: (selectedAnswer: string) => void;
    feedback: string | null;
};

const FlashCardComponent: React.FC<FlashCardProps> = ({ card, onAnswer, feedback }) => (
    <div className="flashcard">
        <div className="flashcard-header">
            <div className="flashcard-title">{card.title}</div>
        </div>
        <div className="flashcard-options">
            {card.options.map((option, index) => (
                <button key={index} onClick={() => onAnswer(option)} className="option-button">
                    {option}
                </button>
            ))}
        </div>
        {feedback && <div className={`feedback ${feedback === "Correct!" ? "correct" : "incorrect"}`}>{feedback}</div>}
    </div>
);

export default PrepareMode;
