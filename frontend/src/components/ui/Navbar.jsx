import { Dumbbell } from "lucide-react";
import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { useLanguage } from "../../context/LanguageContext";
function Navbar() {
  const [isLoggedIn, setIsloggedIn] = useState(false);
  const { language, setLanguage, t } = useLanguage();
  const { token } = useAuth();

  const languages = [
    { code: "en", label: "English" },
    { code: "es", label: "Spanish" },
    { code: "hi", label: "Hindi" },
    { code: "kn", label: "Kannada"}
  ];

  useEffect(() => {
    if (token) {
      setIsloggedIn(true);
    }
  }, []);
  return (
    <nav className="w-full  bg-[#cfb498]  h-15 flex sticky top-0 md:sticky md:top-0 z-99 justify-between items-center  md:flex-row">
      <span className="md:m-4 flex p-2 text-white   md:text-left text-xl md:text-2xl">
        <Dumbbell className="inline mr-2 " size={25} color="white" />
        <p>FORM AI</p>
      </span>
      <div>
        <ul className="flex items-right md:flex-row gap-3 p-2 text-white md:gap-6 md:p-6 text-md md:text-xl">
          {!isLoggedIn ? (
            <>
              <li className="hover:cursor-pointer hover:text-gray-300">
                <Link to="/">Home</Link>
              </li>
              
              
            </>
          ) : (
            <>
            <li className="hover:cursor-pointer hover:text-gray-300">
              <Link to="/dashboard">Home</Link>
            </li>
            <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="px-1  md:px-3 py-1 rounded text-sm font-bold bg-white text-gray-700 hover:bg-gray-100 cursor-pointer outline-none focus:ring-2 focus:ring-blue-500"
            >
                {languages.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                        {lang.label}
                    </option>
                ))}
            </select>
          </>
          )}
          {/* <div className=" hover:cursor-pointer hover:text-gray-300"> */}
          {!isLoggedIn && (
            <>
              <li className="hover:cursor-pointer hover:text-gray-300">
                <Link to="/login/register">{t('navbar_signup')}</Link>
              </li>
              <li className="hover:cursor-pointer hover:text-gray-300">
                <Link to="/Login">{t('navbar_login')}</Link>
              </li>
              {/* Language Toggle Button */}
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="px-1  md:px-3 py-1 rounded text-sm font-bold bg-white text-gray-700 hover:bg-gray-100 cursor-pointer outline-none focus:ring-2 focus:ring-blue-500"
            >
                {languages.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                        {lang.label}
                    </option>
                ))}
            </select>
            </>
          )}
          {/* </div> */}
        </ul>
      </div>
    </nav>
  );
}
export default Navbar;
