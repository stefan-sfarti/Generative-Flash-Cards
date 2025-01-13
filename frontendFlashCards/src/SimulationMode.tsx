import React, { useEffect, useState } from "react";
import "./SimulationMode.css";
import questions from "./questions.json";
import Flashcardlist from "./SimulationFinale.tsx";

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

const App: React.FC<AppProps> = ({ numQuestions }) => {
    const [cards, setCards] = useState<FlashCard[]>([]);
    const [currentCardIndex, setCurrentCardIndex] = useState(0);
    const [feedback, setFeedback] = useState<string | null>(null);
    const [answeres, setAnsweres] = useState<number[]>([]);
    const [cananswer, setCananswer] = useState<number>(0);

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
        setCurrentCardIndex((prev) => (prev === cards.length - 1 ? -1 : prev + 1));
        setFeedback(null);
    };
    const updateAnswerAtIndex = (index: number, newValue: number) => {
        setAnsweres((prevAnsweres) => {
            const updatedAnsweres = [...prevAnsweres];
            updatedAnsweres[index] = newValue;
            return updatedAnsweres;
        });
    };
    const handlePrevious = () => {
        setCurrentCardIndex((prev) => (prev === 0 ? cards.length - 1 : prev - 1));
        setFeedback(null);
    };

    const handleAnswer = (selectedAnswer: string) => {
        if(cananswer<=currentCardIndex && cananswer<cards.length){
            const currentCard = cards[currentCardIndex];
            if (selectedAnswer === currentCard.correctAnswer) {
                setFeedback("Correct!");
                updateAnswerAtIndex(currentCardIndex, 1);
            } else {
                setFeedback("Incorrect!");
                updateAnswerAtIndex(currentCardIndex, 0);
            }
            setCananswer(cananswer + 1);
            handleNext();
        }
        else if(cananswer>currentCardIndex){
            setFeedback("You have already answered this question");
        }
        else if(cananswer>=cards.length){
            setFeedback("You have answered all questions");
        }
    };

    return (
        cards.length > 0 && currentCardIndex != -1 ? (
            <div className="app">
                <div className="header">
                    <p className="header-text">Flash Card</p>
                    <button
                        className="back-button"
                        onClick={() => window.location.replace("/start")}
                    >
                        Back
                    </button>
                </div>

                < div className="body">
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

            </div>
        ) : (
            <Flashcardlist cards={cards} answers={answeres}/>
        )
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

export default App;