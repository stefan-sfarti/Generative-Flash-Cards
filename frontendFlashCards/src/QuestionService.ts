export type Question = {
    id: number;
    question: string;
    answers: string[];
    correctAnswer: string;
};

export type FlashCard = {
    id: number;
    title: string;
    options: string[];
    correctAnswer: string;
};

export const fetchQuestions = async (numQuestions: number): Promise<Question[]> => {
    try {
        const response = await fetch('http://127.0.0.1:8000/question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                difficulty: "medium"
            })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch questions');
        }

        const questions: Question[] = await response.json();
        return questions.slice(0, numQuestions);
    } catch (error) {
        console.error('Error fetching questions:', error);
        throw error;
    }
};