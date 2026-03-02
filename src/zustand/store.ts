import { create } from "zustand";

interface IChapterState {
    currentChapter: number,
    setCurrentChaper: (val:number) => void
}
export const useChapter = create<IChapterState>()((set) =>({
    currentChapter: 0,
    setCurrentChaper: (val) => set(() => ({currentChapter: val}))
}))