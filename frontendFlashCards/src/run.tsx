import React, { useState } from "react";
import App1 from "./PrepareMode.tsx";
import Start from "./Start";
import App2 from "./SimulationMode.tsx";


const Main: React.FC = () => {
    const [numQuestions, setNumQuestions] = useState<number | null>(null);
    const [type, setType] = useState<number | null>(null);
    const handleStart = (questionsCount: number , type: number) => {
        setNumQuestions(questionsCount);
        setType(type)
    };

    return (
            <div>
                {numQuestions === null ? (
                    <Start onStart={handleStart} />
                ) : type === 1 ? (
                    <App1 numQuestions={numQuestions} />
                ) : type === 2 ? (
                    <App2 numQuestions={numQuestions} />
                ) : (
                    <p>Invalid type selected</p>
                )}
            </div>
    );
};

export default Main;