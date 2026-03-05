import { useEffect, useRef, useState } from "react";
import { dataChapters } from "../../data/aiData";
import { useChapter, useUnity } from "../../zustand/store";
import { ChevronLeft } from "lucide-react";

const NavigationBar = () => {
    const { setCurrentChaper, currentChapter } = useChapter();
    const { setVisible, isVisible } = useUnity();
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const dropdownElement = useRef<HTMLDivElement>(null);

    const handleOnChapterClick = (chapterNumber: number) => {
        setIsOpen(false);
        setCurrentChaper(chapterNumber);
    }
    const handleIsOpen = () => setIsOpen(e => !e);
    const handleString = (chapter: string): string => {
        if (chapter.length > 40)
            return chapter.slice(0, 40) + '...';
        else
            return chapter;
    }

    useEffect(() => {
        const handleOutsideClick = (event: MouseEvent) => {
            if (dropdownElement.current && !dropdownElement.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }

        document.addEventListener('mousedown', handleOutsideClick);
        return () => removeEventListener('mousedown', handleOutsideClick);
    }, [])

    return (
        <div className="bg-zinc-800 gold-text">
            <div ref={dropdownElement} className="relative w-auto lg:w-100 cursor-pointer">
                <div className="border flex justify-between  py-4 lg:py-0" onClick={handleIsOpen}>
                    <p className="px-2">{handleString(dataChapters[currentChapter].chapter)}</p>
                    <ChevronLeft className={`transition-transform ${isOpen ? '-rotate-90' : 'rotate-0'}`} />
                </div>
                {
                    <div className={`absolute overflow-hidden duration-300 ${isOpen ? 'max-h-screen' : 'max-h-0 border-b-0 border-t-0'} transition-all top-[calc(100%-1px)] left-0 divide-y border w-full bg-zinc-800`}>
                        {dataChapters.map((chapters, index) =>
                            <p onClick={() => handleOnChapterClick(index)}
                                className={`py-4 lg:py-0 hover:bg-zinc-900 px-2 ${currentChapter === index ? 'bg-zinc-900' : 'bg-zinc-800'}`}
                                key={index}>{handleString(chapters.chapter)}
                            </p>
                        )}
                    </div>
                }   
            </div>

            {/* <button onClick={() => setVisible(!isVisible)}>Toggle Unity Preload</button> */}
        </div>
    )
}

export default NavigationBar;