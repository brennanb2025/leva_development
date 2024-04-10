import './App.css';
import { useState, useEffect, memo } from 'react'
import Matchmaking from './components/Matchmaking'
import Statistics from './components/Statistics';
import Feedback from './components/Feedback';

const ADMIN_ENUM = {
  matchmaking: 1,
  search: 2,
  feedback: 3
}

function App() {

  const [page, setPage] = useState(ADMIN_ENUM.matchmaking)

  const content = () => {
    switch(page){
      case ADMIN_ENUM.matchmaking:
        return <Matchmaking />
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

  return (
    <div className='flex flex-col w-full h-screen'>
      <meta name="csrf-token" content="{{ csrf_token() }}" />
      <section className="w-full p-8">
        <div className="flex flex-row items-center border-b pb-2">
          <div className="matchmaking-header min-w-[15rem]">
            {labeling()}
          </div>
          <button className="option-button" onClick={() => { setPage(ADMIN_ENUM.matchmaking) }}>Matchmaking</button>
          <button className="option-button" onClick={() => { setPage(ADMIN_ENUM.search) }}>User Search</button>
          <button className="option-button" onClick={() => { setPage(ADMIN_ENUM.feedback) }}>Feedback</button>
        </div>
      </section>
      <div className="flex-grow">
        {content()}
      </div>
    </div>
  )
}

export default App;
