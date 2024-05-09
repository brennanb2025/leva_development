import './App.css';
import { useState, useEffect, memo } from 'react'
import Matchmaking from './components/Matchmaking'
import MatchmakingScreen from './components/MatchmakingScreenAnimation';
import Statistics from './components/Statistics';
import Feedback from './components/Feedback';
import axios from 'axios';

const ADMIN_ENUM = {
  matchmaking: 1,
  search: 2,
  feedback: 3
}

function App() {

  const [page, setPage] = useState(ADMIN_ENUM.matchmaking)

  const [matchesMadeScreenVisible, setMatchesMadeScreenVisible] = useState(false);

  function toggleMatchmakingScreenVisibility() {
    setMatchesMadeScreenVisible(true);
    const animationTimeout = setTimeout(() => setMatchesMadeScreenVisible(false), 2499);
    return () => clearTimeout(animationTimeout);
  }

  const getExcelSheet = () => {
    console.log("Getting excel")
    axios.get("/business-excel", { responseType: 'blob' }) // Set responseType to 'blob' to receive binary data
      .then(response => {
          if (response.status === 200) {
              const url = window.URL.createObjectURL(new Blob([response.data]));
              const link = document.createElement('a');
              link.href = url;
              link.setAttribute('download', 'User_data.xls');
              document.body.appendChild(link);
              link.click();
          } else {
              console.log("Error getting excel spreadsheet.")
          }
      })
      .catch(error => {
          // Handle error
          console.error('Error downloading Excel sheet:', error);
      });
  }

  const content = () => {
    switch(page){
      case ADMIN_ENUM.matchmaking:
        return <Matchmaking toggleMatchmakingScreenVisibility={toggleMatchmakingScreenVisibility} />
      case ADMIN_ENUM.search:
        return <Statistics />
      case ADMIN_ENUM.feedback:
        return <Feedback />
    }
  }
  
  const labeling = () => {
    switch(page){
      case ADMIN_ENUM.matchmaking:
        return "Matchmaking"
      case ADMIN_ENUM.search:
        return "User Search"
      case ADMIN_ENUM.feedback:
        return "Feedback"
    }
  }

  const logout = async () => {
    const query = await axios.get("/admin-logout")
    window.location.replace("/admin-login", "_self")
}

  return (
    <div className='flex flex-col w-full h-screen'>
      <MatchmakingScreen animationVisible={matchesMadeScreenVisible} />
      <meta name="csrf-token" content="{{ csrf_token() }}" />
      <section className="w-full p-8">
        <div className="flex flex-row items-center border-b pb-2">
          <div className="matchmaking-header min-w-[15rem]">
            {labeling()}
          </div>
          <button className="option-button" onClick={() => { setPage(ADMIN_ENUM.matchmaking) }}>Matchmaking</button>
          <button className="option-button" onClick={() => { setPage(ADMIN_ENUM.search) }}>User Search</button>
          <button className="option-button" onClick={() => { setPage(ADMIN_ENUM.feedback) }}>Feedback</button>
          <button className="option-button" onClick={getExcelSheet}>Spreadsheet</button>
          <button className="ml-auto text-red-500" onClick={logout}>Logout</button>
        </div>
      </section>
      <div className="flex-grow">
        {content()}
      </div>
    </div>
  )
}

export default App;
