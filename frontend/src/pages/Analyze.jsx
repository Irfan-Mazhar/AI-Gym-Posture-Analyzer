import React, { useEffect, useState } from "react";
import Navbar from "../components/ui/Navbar"
function Analyze() {
  const [liveVideo, setLiveVideo] = useState(false);
  const [reps, setReps] = useState(0);
  const [form, setForm] = useState("N/A");
  const [accuracy, setAccuracy] = useState(0);
  const [exercise, setExercise] = useState(null);
  const [videoSrc, setVideoSrc] = useState("");
  const [detectedExercise, setDetectedExercise] = useState('Detecting...');

  useEffect(() => {
    let eventSource;
    if (liveVideo) {
      // Create a new EventSource connection to our /data route
      eventSource = new EventSource("http://localhost:5000/data");
      console.log("Event source working");

      // Listen for messages from the server
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // Update state with the new data
        setReps(data.reps);
        setForm(data.form);
        setAccuracy(data.accuracy);
        setDetectedExercise(data.exercise || 'Detecting...');
      };

      // Handle any errors
      eventSource.onerror = (err) => {
        console.error("EventSource failed:", err);
        eventSource.close();
      };
    }

    // This cleanup function will be called when the component unmounts
    // or when liveVideo becomes false
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [liveVideo]); // This effect depends on the liveVideo state

  async function startAnalysis() {
    setVideoSrc(`http://localhost:5000/video?t=${new Date().getTime()}`);
    // setExercise(exerciseName);
    setLiveVideo(true);
    setReps(0);
    setForm('N/A');
    setAccuracy(0);
    setDetectedExercise('Detecting...');
  }
  
  async function stopWorkout() {
    setLiveVideo(false);
    setReps(0);
    setForm("N/A");
    setAccuracy(0);
    // setExercise(null);
    await fetch("http://localhost:5000/stop", {
      method: "POST",
    });
  }

  return (
    <div className="bg-white h-screen w-full">
      <Navbar />
      <h1 className="text-blue-500 text-3xl font-heading font-bold mt-10">
        AI Gym Posture Analyzer
      </h1>
      <span>
        {!liveVideo ? (
          <div className="flex flex-col md:block font-heading">
            {/* <h3 className="text-white text-bold font-sans">
              CHOOSE YOUR EXERCISE
            </h3> */}

            <button 
              className="border-2 font-bold bg-red-500 m-4 hover:shadow-lg shadow-gray-500/80 rounded-lg p-3 hover:cursor-pointer hover:scale-[1.05]"
              onClick={startAnalysis}
            >Start Analysis</button>
            {/* <button
              className="border-2 font-bold bg-red-500 m-4 hover:shadow-lg shadow-gray-500/80 rounded-lg p-3 hover:cursor-pointer hover:scale-[1.05]"
              onClick={() => startWorkout("pushups")}
            >
              Push Ups
            </button>
            <button
              className="border-2  font-bold   bg-red-500 m-4 hover:shadow-lg shadow-gray-500/80 rounded-lg p-3 hover:cursor-pointer hover:scale-[1.05]"
              onClick={() => startWorkout("squats")}
            >
              Squats
            </button>
            <button
              className="border-2  hover:scale-[1.05] font-bold bg-red-500 m-4 hover:shadow-lg shadow-gray-500/80 rounded-lg p-3 hover:cursor-pointer"
              onClick={() => startWorkout("curls")}
            >
              Bicep Curls
            </button>
            <button
              className="border-2  font-bold   bg-red-500 m-4 hover:shadow-lg shadow-gray-500/80 rounded-lg p-3 hover:cursor-pointer hover:scale-[1.05]"
              onClick={() => startWorkout("shoulderpress")}
            >
              Shoulder Press
            </button> */}
          </div>
        ) : (
          <button
            className="border-2 font-bold hover:shadow-lg shadow-gray-500/80 bg-red-500 rounded-lg p-3 hover:cursor-pointer"
            onClick={stopWorkout}
          >
            Stop Workout
          </button>
        )}
      </span>
      <div className="flex flex-col lg:flex-row items-center lg:items-stretch justify-center">
        {liveVideo === true ? (
          <div className="m-4 mb-2 ">
            <img
              src={videoSrc}
              alt="AI Gym Trainer"
              className="rounded-lg shadow-lg border-4 border-orange-500  "
            />
          </div>
        ) : (
          <div></div>
        )}
        {liveVideo && (
          <div className="m-3  p-4 bg-gray-800 rounded-lg shadow-lg text-left text-2xl w-80 text-white font-heading">
            <h2 className="text-3xl font-bold mb-3 text-orange-500 text-center">{detectedExercise.replace('_',' ').toUpperCase()} Stats</h2>
            <h2 className="text-3xl font-bold mb-3 text-orange-500 text-center">
              WORKOUT STATS
            </h2>
            <div className="mb-2">
              <p className="font-semibold font-sans">REPS:</p>
              <p className="text-3xl font-bold text-green-400">{reps}</p>
            </div>
            <div className="mb-2">
              <p className="font-semibold font-sans">FORM:</p>
              <p
                className={`text-3xl font-bold ${
                  form === "Good Form" || form === "Good Depth"
                    ? "text-green-400"
                    : "text-red-500"
                }`}
              >
                {form}
              </p>
            </div>
            <div>
              <p className="font-semibold font-sans">ACCURACY:</p>
              <p
                className={`text-3xl font-bold ${
                  accuracy > 85 ? "text-green-400" : "text-yellow-500"
                }`}
              >
                {accuracy}%
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
export default Analyze;
