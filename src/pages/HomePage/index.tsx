import React from "react";
import { dataChapters } from "../../data/aiData";
import { useChapter } from "../../zustand/store";

const HomePage = () => {
    const renderContent = (contentArray: string[]): React.ReactNode[] => {
        const result: React.ReactNode[] = [];
        let bulletItems: React.ReactNode[] = [];
        let bulletItemsNested: React.ReactNode[] = [];
        let numberItems: React.ReactNode[] = [];
        let inBulletList = false;
        let inNumberList = false;
        let inBulletNested = false;

        contentArray.forEach((content, idx) => {
            // Handle start/end tags first
            if (content === '--bullet-start') {
                inBulletList = true;
            }
            else if (content === "--number-start") {
                inNumberList = true;
            }
            else if (content === "--bullet-start-nested") {
                inBulletNested = true;
            }
            else if (content === '--bullet-end-nested') {
                if (bulletItemsNested.length > 0) {
                    bulletItems.push(
                        <ul className="list-[circle] ml-4" key={`ul-nested-${idx}`}>
                            {bulletItemsNested}
                        </ul>
                    );
                    bulletItemsNested = [];
                }
                inBulletNested = false;
            }
            else if (content === '--bullet-end') {
                if (bulletItems.length > 0) {
                    result.push(
                        <ul className="list-disc" key={`ul-${idx}`}>
                            {bulletItems}
                        </ul>
                    );
                    bulletItems = [];
                }
                inBulletList = false;
            }
            else if (content === '--number-end') {
                if (numberItems.length > 0) {
                    result.push(
                        <ol className="list-decimal" key={`ol-${idx}`}>
                            {numberItems}
                        </ol>
                    );
                    numberItems = [];
                }
                inNumberList = false;
            }
            // Handle content
            else if (inBulletNested) {
                bulletItemsNested.push(
                    <li key={`li-${idx}`} className="ml-4">{content}</li>
                );
            }
            else if (inBulletList) {
                bulletItems.push(
                    <li key={`li-${idx}`} className="ml-4">{content}</li>
                );
            }
            else if (inNumberList) {
                numberItems.push(
                    <li key={`li-${idx}`} className="ml-4">{content}</li>
                );
            }
            else {
                if (content === '--space')
                    result.push(<br key={`space-${idx}`} />);
                else
                    result.push(
                        <div key={`text-${idx}`}>{content}</div>
                    );
            }
        });

        return result;
    };

    const { currentChapter } = useChapter();
    return (
        <div className="flex flex-col w-auto lg:w-170 px-5">
            {dataChapters && dataChapters[currentChapter] &&
                <div>
                    <div className="flex flex-col">
                        <h2 className="text-2xl gold-text">{dataChapters[currentChapter].chapter}</h2>
                        <h3 className="text-xl italic text-zinc-50">"{dataChapters[currentChapter].subTopics.header}"</h3>
                    </div>
                    <div>
                        {renderContent(dataChapters[currentChapter].subTopics.content)}
                    </div>
                </div>
            }
        </div>
    );
}

export default HomePage;