import { Link } from "react-router-dom";
import { useCallback } from 'react';
import Particles from "react-tsparticles";
import {loadSlim} from "tsparticles-slim";
function Hero() {
  const particlesInit = useCallback(async (engine) => {
    await loadSlim(engine);
  }, []);

  // 👇 Particle options with dumbbell image shape
  const particleOptions = {
  fullScreen: { enable: false },
  particles: {
    number: {
      value: 15,
      density: { enable: true, area: 800 },
    },
    color: "#cfb498",
    shape: {
      type: "image",
      image: [
        {
          src: "/dumbbell.svg", // 👉 your dumbbell image
          width: 26,
          height: 26,
        },
      ],
    },
    opacity: { value: 0.8 },
    size: {
      value: 8,
      random: { enable: true, minimumValue: 23 },
    },
    move: {
      enable: true,
      speed: 2,
      direction: "none",
      outModes: { default: "bounce" },
    },
  },
  detectRetina: true,
};

  return (
    <div className="h-full mt-40 md:mt-0 md:flex md:flex-col md:items-center">
      <Particles
        id="tsparticles"
        init={particlesInit}
        options={particleOptions}
        className="absolute hidden md:block top-0 left-0 w-full h-full z-[0]"
      />

      {/* Header Section */}
      <div className="z-1 ">
        <h1 className="text-[#cfb498] bg-white z-1 text-5xl md:text-6xl md:mt-40 md:mb-20 font-bold font-serif">WELCOME TO FORM AI</h1>
      </div>
      {/* Demo Video*/}
      <div className="flex md:w-300  flex-col md:flex-row items-center md:justify-between justify-center md:flex-row md:justify-center md:items-start  ">
        <div className="md:flex bg-white z-1 md:flex-col items-center justify-center">
          <div className=" shadow-xl  border-white rounded-lg p-3 m-4  mt-10 mb-2   hover:text-white text-black h-50 md:h-90 md:w-150">
            <video src="/demo-video.mp4" loop muted autoPlay className="fit-cover"></video>
          </div>
          <p className="text-gray-300 text-md italic md:text-2xl text-center md:ml-14">Demo Video</p>
        </div>
        {/* Description Section */}
        <div className="bg-white z-1">
          <p className="text-[#cfb498] text-xl m-3 md:text-left">
            Can't afford a personal trainer? No worries, we've got you covered!
            Our AI-powered personal trainer is here to help you achieve your
            fitness goals with personalized workout plans, real-time feedback on
            your form, and progress tracking.
          </p>
          <p className="hidden md:block text-[#cfb498] text-xl m-3 md:text-left">
            Lorem ipsum dolor sit amet consectetur, adipisicing elit. Ut explicabo rem dignissimos atque molestias perspiciatis nisi saepe assumenda, minima in, quos distinctio, maiores inventore dolor facere dolorum quia corrupti nesciunt!
          </p>
          <div className="flex justify-center items-center md:justify-start focus:none">
            <Link
              to="/analyze"
              className="text-white animate-pulse focus:none border-2 hover:cursor-pointer bg-[#cfb498] p-3 rounded-3xl md:flex w-fit"
            >
              Try Now!
            </Link>
          </div>
        </div>
      </div>
      </div>
  );
}
export default Hero;
