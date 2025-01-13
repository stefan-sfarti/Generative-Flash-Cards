import React from 'react';
import './SimulationFinale.css';

type FlashCard = {
    id: number;
    title: string;
    options: string[];
    correctAnswer: string;
};

type Props = {
    cards: FlashCard[];
    answers: number[];
};

const FlashCardList: React.FC<Props> = ({ cards, answers }) => {
    const indexArray = Array.from({ length: cards.length }, (_, index) => index);

    // Calculăm numărul de răspunsuri corecte
    const correctAnswersCount = answers.filter(answer => answer === 1).length;

    return (
        <div style={{ height: '100vh' }}>
            <div className="header">
                <h1 style={{ marginTop: '.20em' }}>
                    FLASH CARD - {correctAnswersCount}/{cards.length}
                </h1>
                <button
                    className="back-button"
                    onClick={() => window.location.replace("/start")}
                >
                    Back
                </button>
            </div>
            <div className="flash-card-list">
                <div className="card-list">
                    {indexArray.map((index) => (
                        <div key={cards[index].id} className="card">
                            <div className="card-info">
                                <h3>{cards[index].title}</h3>
                                <p>{cards[index].correctAnswer}</p>
                            </div>
                            <div className="card-meta">
                                <p className={answers[index] === 1 ? "correct" : "incorrect"}>
                                    {answers[index] === 1 ? "Correct" : "Incorrect"}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default FlashCardList;
