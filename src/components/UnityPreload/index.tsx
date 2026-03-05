import { useUnity } from "../../zustand/store";

const UnityPreload = () => {
    const { isVisible } = useUnity();
    return (

        <div className={`${isVisible ? 'opacity-100 left-0 top-0' : 'opacity-0 left-full top-0'} absolute`} style={{ width: "100%", height: "100vh" }}>
            <iframe
                src="https://scaniaweb.s3.eu-north-1.amazonaws.com/AccessoriesConfigurator_0.1.1_0_Web/index.html"
                width="100%"
                height="100%"
                style={{ border: "none" }}
                title="Unity Game"
                allowFullScreen
            />
        </div>
    );
}

export default UnityPreload;    