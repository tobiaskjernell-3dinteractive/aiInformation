import { dataChapters } from "../../data/aiData";
import { useChapter } from "../../zustand/store";

const NavigationBar = () => {
  const {setCurrentChaper} = useChapter();
    return (
        <div className="bg-zinc-800 gold-text">
            <select onChange={(e) => {setCurrentChaper(Number(e.target.value))}} className="border p-2 bg-zinc-800 w-full lg:w-auto">
                {dataChapters.map((item, index) => 
                <option className="w-auto" key={index} value={index} >{item.chapter}</option>)}
            </select>
        </div>
    )
}

export default NavigationBar;