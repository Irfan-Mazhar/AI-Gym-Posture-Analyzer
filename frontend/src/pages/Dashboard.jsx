import { useEffect, useState } from "react";
import Navbar from "../components/ui/Navbar";
import { useAuth } from "../context/AuthContext";
import { Link } from "react-router-dom";


function Dashboard() {
    const { token, logout } = useAuth(); // Get token and logout function from context
    const [profileData, setProfileData] = useState(null); // State to store user profile
    const [isLoading, setIsLoading] = useState(true); // State to manage loading indicator
    const [error, setError] = useState(null); // State to store potential errors

    // --- Fetch Profile Data on Component Mount ---
    useEffect(() => {
        const fetchProfile = async () => {
            if (!token) {
                setIsLoading(false);
                setError("No token found. Please log in.");
                // Optional: You might redirect to login here if token is missing unexpectedly
                return;
            }

            setIsLoading(true); // Start loading
            setError(null);

            try {
                const response = await fetch('http://localhost:5000/profile', {
                    method: 'GET',
                    headers: {
                        // Include the JWT token in the Authorization header
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    setProfileData(data.user_data); // Store the user data
                } else if (response.status === 401 || response.status === 403) {
                    // Handle unauthorized access (e.g., expired token)
                    setError("Session expired or invalid. Please log in again.");
                    logout(); // Log the user out using the context function
                } else {
                    // Handle other server errors
                    const errorData = await response.json();
                    setError(errorData.message || 'Failed to fetch profile.');
                }
            } catch (err) {
                console.error("Fetch profile error:", err);
                setError('An error occurred while fetching your profile.');
            } finally {
                setIsLoading(false); // Stop loading regardless of outcome
            }
        };

        fetchProfile();
    }, [token, logout]); // Re-run effect if token changes
    return(
        <div className="w-full h-screen bg-white ">
            <Navbar />
            <h1 className="text-[#cfb498] mt-10 font-bold text-5xl ">Welcome {profileData?.username}</h1>
            <div className="border-2 border-black rounded-md p-2 bg-[#cfb498] text-xl text-left w-100 mx-auto mt-20">
                <h2 className="text-2xl text-center font-semibold">User Data:</h2>
                <p>Age: {profileData?.age}</p>
                <p>Height: {profileData?.height}cm</p>
                <p>Weight: {profileData?.weight}kg</p>
                <p>BMI: {profileData?.bmi}</p>
            </div>
            <div className="mt-30">

             <Link
              to="/analyze"
              className="text-white p-3  animate-pulse focus:none border-2 hover:cursor-pointer bg-[#cfb498]  rounded-3xl "
              >
              Start a Workout Session!
            </Link>
                </div>
        </div>
    )
}
export default Dashboard;