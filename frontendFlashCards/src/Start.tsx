import React from "react";
import "./styles/Start.css";

type StartProps = {
    onStart: (questionsCount: number, type: number) => void;
};

const Start: React.FC<StartProps> = ({ onStart }) => {
    return (
        <div className="container">
            <div className="mode-section">
                <h2>Prepare Mode</h2>
                <p>How many questions?</p>
                <div className="button-group">
                    <button className="option-button" onClick={() => onStart(25,1)}>25</button>
                    <button className="option-button" onClick={() => onStart(50,1)}>50</button>
                    <button className="option-button" onClick={() => onStart(100,1)}>100</button>
                </div>
            </div>
            <div className="mode-section">
                <h2>Simulation Mode</h2>
                <p>How many questions?</p>
                <div className="button-group">
                    <button className="option-button" onClick={() => onStart(25,2)}>25</button>
                    <button className="option-button" onClick={() => onStart(50,2)}>50</button>
                    <button className="option-button" onClick={() => onStart(100,2)}>100</button>
                </div>
            </div>
        </div>
    );
};

export default Start;
