import { Dumbbell } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState,useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
function Navbar() {
    const [isLoggedIn, setIsloggedIn] = useState(false);
    const {token} = useAuth();
    useEffect(() => {
        if(token){
            setIsloggedIn(true);
        }
    },[])
    return (
        <nav className="w-full  bg-[#cfb498]  h-15 flex sticky top-0 md:sticky md:top-0 z-99 justify-between items-center  md:flex-row">
                <span className="md:m-4 flex p-2 text-white   md:text-left text-xl md:text-2xl">
                    <Dumbbell className="inline mr-2 " size={25} color="white" />
                    <p>FORM AI
                    </p>

                </span>
                <div>
                    <ul className="flex items-right md:flex-row gap-3 p-2 text-white md:gap-6 md:p-6 text-md md:text-xl">
                        {!isLoggedIn?
                        <>
                        <li  className='hover:cursor-pointer hover:text-gray-300'>
                           <Link to="/">Home</Link> 
                        </li>
                        <li className='hover:cursor-pointer hover:text-gray-300'>
                            About
                        </li>
                        </>:
                        <li className='hover:cursor-pointer hover:text-gray-300'><Link to="/dashboard">Home</Link></li>
                        }
                        {/* <div className=" hover:cursor-pointer hover:text-gray-300"> */}
                        {!isLoggedIn &&
                        <>
                        <li className='hover:cursor-pointer hover:text-gray-300'>
                            <Link to="/login/register">Sign Up</Link>
                        </li>
                        <li className='hover:cursor-pointer hover:text-gray-300'>
                            <Link to="/Login">Login</Link>
                        </li>
                        </>
                        }
                        {/* </div> */}
                    </ul>
                </div>
            </nav>
    )
}
export default Navbar;