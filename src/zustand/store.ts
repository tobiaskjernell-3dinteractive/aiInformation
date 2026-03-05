import { create } from "zustand";

interface IChapterState {
    currentChapter: number,
    setCurrentChaper: (val:number) => void
}

interface IUnity {
    isVisible: boolean,
    setVisible: (value:boolean) => void
}
export const useChapter = create<IChapterState>()((set) =>({
    currentChapter: 0,
    setCurrentChaper: (val) => set(() => ({currentChapter: val}))
}))

export const useUnity = create<IUnity>()((set) => ({
    isVisible: false,
    setVisible: (val) => set(() => ({isVisible: val}))
}))